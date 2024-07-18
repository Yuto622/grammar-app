from itertools import zip_longest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import matplotlib.pyplot as plt
import io
import urllib, base64
from charts.models import Chart


@login_required(login_url='/users/sign_in/')
def index(request):
    individual_durations = []
    individual_word_counts = []
    individual_sentence_counts = []
    individual_error_counts = []

    part_records = Chart.objects.order_by('user_id')

    current_user_id = None
    current_duration_list = None
    current_word_count_list = None
    current_sentence_count_list = None
    current_error_count_list = None

    part = 0
    part_max = 0
    for record in part_records:
        if record.user_id != current_user_id:
            part_max = 0
            if current_user_id is not None:
                individual_durations.append(current_duration_list)
                individual_word_counts.append(current_word_count_list)
                individual_sentence_counts.append(current_sentence_count_list)
                individual_error_counts.append(current_error_count_list)

            current_user_id = record.user_id
            current_duration_list = []
            current_word_count_list = []
            current_sentence_count_list = []
            current_error_count_list = []

        current_duration_list.append(record.duration)
        current_word_count_list.append(record.word_count)
        current_sentence_count_list.append(record.sentence_count)
        current_error_count_list.append(record.error_count)
        part_max += 1
        part = part_max if part_max > part else part

    if current_user_id is not None:
        individual_durations.append(current_duration_list)
        individual_word_counts.append(current_word_count_list)
        individual_sentence_counts.append(current_sentence_count_list)
        individual_error_counts.append(current_error_count_list)
    individual_durations = map_data(individual_durations)
    individual_word_counts = map_data(individual_word_counts)
    individual_sentence_counts = map_data(individual_sentence_counts)
    individual_error_counts = map_data(individual_error_counts)
    average_duration = average_data(individual_durations)
    average_word_count = average_data(individual_word_counts)
    average_sentence_count = average_data(individual_sentence_counts)
    average_error_counts = average_data(individual_error_counts)
    print(individual_durations)
    print(individual_word_counts)
    print(individual_sentence_counts)
    print(individual_error_counts)
    print(average_duration)
    print(average_word_count)
    print(average_sentence_count)
    print(average_error_counts)
    parts = ['{}'.format(i) for i in range(1, part + 1)]
    fig, ax1 = plt.subplots(figsize=(20, 12))

    # Plot bar graph for average duration
    bars = ax1.bar(parts, average_duration, color='lightblue', label='Average Duration (seconds)')
    ax1.set_xlabel('Parts')
    ax1.set_ylabel('Duration (seconds)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Plot individual durations
    for part, durations in zip(parts, individual_durations):
        ax1.scatter([part] * len(durations), durations, color='blue', alpha=0.6)

    # Create second y-axis for word and sentence count
    ax2 = ax1.twinx()
    ax2.set_ylabel('Word, Sentence and error Count', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    # Plot line graphs for average word count and sentence count
    ax2.plot(parts, average_word_count, color='green', marker='o', label='Average Word Count')
    ax2.plot(parts, average_sentence_count, color='red', marker='x', label='Average Sentence Count')
    ax2.plot(parts, average_error_counts, color='#000000', marker='*', label='Average error Count')

    # Plot individual word counts and sentence counts
    for part, word_counts, sentence_counts, error_counts in zip(parts, individual_word_counts,
                                                                individual_sentence_counts, individual_error_counts):
        ax2.scatter([part] * len(word_counts), word_counts, color='green', alpha=0.6)
        ax2.scatter([part] * len(sentence_counts), sentence_counts, color='red', alpha=0.6)
        ax2.scatter([part] * len(error_counts), error_counts, color='#000000', alpha=0.6)

    fig.legend(loc='upper right', bbox_to_anchor=(1, 1.11), bbox_transform=ax1.transAxes)

    # Set the title below the plot
    fig.suptitle('Average and Individual Video Transcript Analysis by Part', y=0.93)

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plt.close(fig)

    return render(request, 'charts.html', {'data': uri})


def average_data(array):
    result = []
    for subarr in array:
        if len(subarr) > 0:
            avg = sum(subarr) / len(subarr)
            result.append(avg)
    return result


def map_data(array):
    result = list(zip_longest(*array, fillvalue=None))
    result = [[item for item in sublist if item is not None] for sublist in result]
    return result
