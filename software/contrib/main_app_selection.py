from europi import *
from time import sleep_ms, ticks_diff, ticks_ms
import example_app, coin_toss, radio_scanner, consequencer, diagnostic, machine

def app_confirm():
    global app_flg
    print('fall')
    app_flg = 1
    
def reset():
    print('longer')
    oled.centre_text('Reset...')
    sleep_ms(1500)
    reset_state()
    init()
    
def init():
    global rect_pos, text_pos, app_text, app_idx, app_flg
    
    machine.freq(250_000_000)
    b2.handler_falling(app_confirm)
    b2.handler_longer(reset)
    
    rect_pos = [[2, 8], [8, 20]]
    text_pos = [[10, 10], [10, 22]]
    app_text = ['Example App', 'Coin Toss', 'Radio Scanner', 'Consequencer', 'Diagnostic']
    app_idx = 0
    app_flg = 0

def main():
    global rect_pos, text_pos, app_text, app_idx, app_flg
    
    init()
    while True:
        if app_flg == 0:
            # App selection
            app_idx = k2.choice([i for i in range(len(app_text))])
            
            # OLED Show
            oled.fill(0)
            if app_idx == len(app_text) - 1:
                oled.text(app_text[app_idx - 1], text_pos[0][0], text_pos[0][1], 1)
                
                oled.fill_rect(rect_pos[1][0], rect_pos[1][1], 120, 12, 1)
                oled.text(app_text[app_idx], text_pos[1][0], text_pos[1][1], 0)
            else:
                oled.fill_rect(rect_pos[0][0], rect_pos[0][1], 120, 12, 1)
                oled.text(app_text[app_idx], text_pos[0][0], text_pos[0][1], 0)
                
                oled.text(app_text[app_idx+1], text_pos[1][0], text_pos[1][1], 1)
        else:
            # Jump to target app
            if app_idx == 0:
                app_flg = example_app.run()
                reset_state()
                init()
            elif app_idx == 1:
                app_flg = coin_toss.run()
                reset_state()
                init()
            elif app_idx == 2:
                app_flg = radio_scanner.run()
                reset_state()
                init()
            elif app_idx == 3:
                app_flg = consequencer.run()
                reset_state()
                init()
            elif app_idx == 4:
                app_flg = diagnostic.run()
                reset_state()
                init()
            else:
                app_flg = 0
                
        oled.show()
        sleep_ms(100)
                    
if __name__ == "__main__":
    main()
