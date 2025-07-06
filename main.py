import csv
import yaml
import random

from typing import List, Dict
from os.path import join

from psychopy import visual, monitors, event, logging, gui, core

def save_results() -> None:
    """
    Save results of experiment. Decorated with @atexit in order to make sure that intermediate
    results will be saved even if interpreter will break.

    Returns:
        Nothing.
    """

    file_name = PART_ID + '_' + str(random.randint(100, 999)) + '_beh.csv'
    with open(join('.', file_name), 'w', encoding='utf-8') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(RESULTS)

def check_exit(key: str = 'f7') -> None:
    """
    Check if exit button pressed.

    Returns:
        Nothing.
    """
    stop = event.getKeys(keyList=[key])
    if stop:
        abort_with_error('Experiment finished by user! {} pressed.'.format(key))

def collect_pos(start, end) -> List[float]:
    start_to_hatch = (conf['NL_ABS_LENGTH'] / 2) + hatchMark.pos[0]
    line_fraction = start_to_hatch / conf['NL_ABS_LENGTH']
    nl_pos = (end - start) * line_fraction + start
    return line_fraction, nl_pos


def monitor_hatch(number) -> (float, float):

    # Prepare all variables
    ready_click_time = 0
    monitorClock.reset()
    hatchMark.pos = (conf['NL_ABS_LENGTH']/-2, 0)

    while True:
        check_exit()

        # Highlight button if mouse hovers over
        if ready.contains(mouse):
            ready.borderWidth = 1.5
            ready.borderColor = conf['HIGHLIGHT_COLOR']
            ready.color = conf['HIGHLIGHT_COLOR']

            # If ready pressed exit the loop, but only after making a mark
            if mouse.isPressedIn(ready, buttons=[0]) and hatchMark.pos is (conf['NL_ABS_LENGTH']/-2, 0):
                makeMarkdown.draw()
                win.flip()
                core.wait(3)
                draw(stimuli)
                mouse.clickReset()
            elif mouse.isPressedIn(ready, buttons=[0]) and not hatchMark.pos is (conf['NL_ABS_LENGTH']/-2, 0):
                mouse.clickReset()
                break

        else:
            ready.borderWidth = 0
            ready.color = conf['BACKGROUND_COLOR']

        if mouse.isPressedIn(nlShadow, buttons=[0]):
            mouse_pos = mouse.getPos()
            hatchMark.pos = (mouse_pos[0], 0)
            ready_click_time = monitorClock.getTime()
            mouse.clickReset()

        draw(stimuli)
    return ready_click_time, monitorClock.getTime()

def draw(stimuli) -> None:
    [obj.draw() for obj in stimuli]
    win.flip()

# === Dialog popup ===
info: Dict = {'ID': '', 'Sex': ['M', 'F'], 'Age': '20'}
dict_dlg = gui.DlgFromDict(dictionary=info, title='Experiment title, fill by your name!')
if not dict_dlg.OK:
    raise 'Info dialog terminated.'
PART_ID = info['ID'] + '_' + info['Age'] + info['Sex']

# load config, all params should be there
conf: Dict = yaml.load(open('config.yaml', encoding='utf-8'), Loader=yaml.SafeLoader)
frame_rate: int = conf['FRAME_RATE']
SCREEN_RES: List[int] = conf['SCREEN_RES']

# check config
for value in conf.keys():
    if value in ['SCREEN_RES']:
        continue
    elif isinstance(conf[value], list) and not len(conf[value]) == conf['NO_BLOCKS']:
        raise Exception(value)

# prepare results template
RESULTS = list()  # list in which data will be collected
RESULTS.append(['PART_ID',
                'Block_no'
                'Trial_no',
                'Target_no',
                'Target_fr',
                'Marked_no',
                'Marked_fr',
                'Marked_time',
                'Click_time'])  # Results header

# === Scene init ===
testMonitor = monitors.Monitor(name = 'testMonitor',)
testMonitor.setWidth(conf['MONITOR_WIDTH'])
testMonitor.setSizePix(SCREEN_RES)

win = visual.Window(SCREEN_RES,
                    fullscr=True,
                    monitor=testMonitor,
                    units='cm',
                    color=conf['BACKGROUND_COLOR'])
win.setColor(conf['BACKGROUND_COLOR'])
mouse = event.Mouse(visible=True, newPos=(0,0), win=win)  # Make mouse invisible
clock = core.Clock()
monitorClock = core.Clock()



# === Prepare stimulus here ===
numberLine = visual.Line(win,
                        name='numberLine',
                        units='cm',
                        start = (-1 * conf['NL_ABS_LENGTH']/2 , 0),
                        end = (conf['NL_ABS_LENGTH']/2, 0),
                         color = conf['BACKGROUND_COLOR'])
numberLine.setColor(conf['STIM_COLOR'])

nlShadow = visual.Rect(win,
                       name='nlShadow',
                       units='cm',
                       width = conf['NL_ABS_LENGTH'],
                       height = conf['HATCH_LENGTH'],)
nlShadow.setColor(conf['BACKGROUND_COLOR'])

hatchMark = visual.Line(win,
                        name='hatchMark',
                        units='cm',
                        start = (0, conf['HATCH_LENGTH']/2),
                        end = (0, -1 * conf['HATCH_LENGTH']/2),)
hatchMark.setColor(conf['HATCH_COLOR'])

ready = visual.TextBox2(win,
                        name='readyButton',
                        units='norm',
                        pos=(2/3, -2/3),
                        size=(conf['READY_LETTER']/1.5 * len(conf['READY_MSG']), 0.2),
                        fillColor=conf['STIM_COLOR'],
                        borderColor = conf['HIGHLIGHT_COLOR'],
                        borderWidth=0,

                        text=conf['READY_MSG'],
                        letterHeight=conf['READY_LETTER'],
                        bold=True,
                        alignment='center',
                        color = conf['BACKGROUND_COLOR'])

makeMarkdown = visual.TextBox2(win,
                               units='norm',
                               size=(1.7, None),
                               fillColor=conf['HATCH_COLOR'],
                               borderColor=conf['HIGHLIGHT_COLOR'],

                               text='Zaznacz pozycję liczby!',
                               color=conf['HIGHLIGHT_COLOR'],
                               bold=True,
                               alignment='center',
                               letterHeight=0.2,)
targetNumber = visual.TextBox2(win,
                                 units='norm',
                                 pos=(0, 0.5),
                                 letterHeight=0.2,
                                 color=conf['STIM_COLOR'],
                                 bold=True,
                                 text='wait_for_number',
                                 alignment='center',)

lineStart = visual.TextBox2(win,
                                 units='cm',
                                 pos=(conf['NL_ABS_LENGTH']/-2, conf['HATCH_LENGTH'] * 1.5),
                                 letterHeight=conf['HATCH_LENGTH'],
                                 color=conf['STIM_COLOR'],
                                 text='wait_for_number',
                                 alignment='center',)

lineEnd = visual.TextBox2(win,
                                 units='cm',
                                 pos=(conf['NL_ABS_LENGTH']/2, conf['HATCH_LENGTH'] * 1.5),
                                 letterHeight=conf['HATCH_LENGTH'],
                                 color=conf['STIM_COLOR'],
                                 text='wait_for_number',
                                 alignment='center')

prepareScreen = visual.TextBox2(win,
                                units='norm',
                                letterHeight=0.1,
                                text='Poczekaj na próbę',
                                color=conf['STIM_COLOR'],
                                alignment='center')

welcomeScreen = visual.TextBox2(
    win,
    units='norm',
    pos=(0, 0),
    size=(1.6, 1.2),
    letterHeight=0.06,
    alignment='center',
    lineSpacing=1.1,
    color=conf['STIM_COLOR'],
    text=(
        "W trakcie badania prezentowana Ci będzie oś liczbowa "
        "o oznaczonym początku oraz końcu.\n\n"
        "Twoim zadaniem jest odczytać umieszczoną nad nią wartość liczbową "
        "i nanieść ją na oś za pomocą lewego przycisku myszy.\n\n"
        "Kiedy będziesz gotowx, kliknij spację."
    )
)

# Display instructions
welcomeScreen.draw()
win.flip()
while True:
    check_exit()
    if len(event.getKeys('space')) > 0:
        event.clearEvents()
        break

# Initialize main loop for blocks
for i in range(conf['NO_BLOCKS']):
    start, end = conf['NL_START_END'][i]
    lineStart.text = start
    lineEnd.text = end

    # Prepare number list including wanted numbers
    # Not yet handling banned fractions :(
    how_many_generate = conf['BLOCK_LENGTH'][i] - len(conf['WANTED_NUMBERS'][i])
    if conf['ONLY_WHOLE_NUMBERS'][i]:
        numbers = random.sample(range(start, end), how_many_generate)
        fractions = [number / (end - start) for number in numbers]
    else:
        fractions = [random.random() for _ in range(how_many_generate)]
        numbers = [(end - start) * fraction + start for fraction in fractions]

    numbers += conf['WANTED_NUMBERS'][i]
    random.shuffle(numbers)

    # prepare objects to display
    stimuli = [nlShadow, numberLine, hatchMark, ready , lineStart, lineEnd]
    if conf['NUMBER_TO_POS'][i]:
        stimuli.append(targetNumber)

    # initialize trial loop
    for j in range(conf['BLOCK_LENGTH'][i]):

        # display prepare screen
        prepareScreen.draw()
        win.flip()
        core.wait(3)

        number = numbers[j]
        fraction = fractions[j]
        targetNumber.text = number
        mouse.clickReset()
        Marked_time, Click_time = monitor_hatch(number)
        Marked_fr, Marked_no = collect_pos(start, end)
        RESULTS.append([PART_ID,  # add results to master list
                        i + 1,
                        j + 1,
                        number,
                        fraction,
                        Marked_no,
                        Marked_fr,
                        Marked_time,
                        Click_time])
save_results()
