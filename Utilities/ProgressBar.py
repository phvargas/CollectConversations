def display_progress_bar(bar_size=20, percent=0.50):
    fill_boxes = int(bar_size * percent)
    unfilled = bar_size - fill_boxes
    print('▓' * fill_boxes, end='')
    perc_value = percent * 100
    if perc_value > 100:
        perc_value = 100
    print('{} {:.0f}%'.format('░' * unfilled, perc_value), end='\r', flush=True)
