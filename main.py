import os
import asyncio
import tzlocal
from bot import reload_page, connect_wallet, login_metamask, treasure_hunt_game, new_map, skip_error_on_game, refresh_hereoes_positions, send_heroes_to_work, first_start, SetTrigger
from controllers import get_browser, countdown_timer, setup_logger, initialize_pyautogui, read_configurations, delete_log_files, delete_folders
from pywinauto import Desktop
from itertools import cycle
from apscheduler.schedulers.background import BackgroundScheduler

try:
    streamConfig = read_configurations()
    refresh_heroes_time = streamConfig['heroes_options']['refresh_heroes_time']
    refresh_heroes_only = streamConfig['heroes_options']['refresh_heroes_only']
    work_heroes_time = streamConfig['heroes_options']['work_heroes_time']
    refresh_browser_time = streamConfig['bot_options']['refresh_browser_time']
    enable_multiaccount = streamConfig['bot_options']['enable_multiaccount']
except FileNotFoundError:
    print('Error: config.yaml file not found, make sure config.yaml are placed in the folder..')
    exit()

async def main():
    logger = setup_logger(telegram_integration=True)

    # Init message
    print('\nPress Ctrl-C to quit at anytime!\n' )

    hello_world = """
    #******************************* BombCrypto Bot *********************************#
    #────────────────────────────────────────────────────────────────────────────────#
    #─────██████████████───██████████████─██████──────────██████─██████████████──────#
    #─────██░░░░░░░░░░██───██░░░░░░░░░░██─██░░███────────███░░██─██░░░░░░░░░░██──────#
    #─────██░░██████░░██───██░░██████░░██─██░░░███──────███░░░██─██░░██████░░██──────#
    #─────██░░██──██░░██───██░░██──██░░██─██░░░░███────███░░░░██─██░░██──██░░██──────#
    #─────██░░██████░░████─██░░██──██░░██─██░░░░░░██──███░░░░░██─██░░██████░░████────#
    #─────██░░░░░░░░░░░░██─██░░██──██░░██─██░░░░██████████░░░░██─██░░░░░░░░░░░░██────#
    #─────██░░████████░░██─██░░██──██░░██─██░░░░██─████─██░░░░██─██░░████████░░██────#
    #─────██░░██────██░░██─██░░██──██░░██─██░░░░██──██──██░░░░██─██░░██────██░░██────#
    #─────██░░████████░░██─██░░██████░░██─██░░░░██──────██░░░░██─██░░████████░░██────#
    #─────██░░░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░██──────██░░░░██─██░░░░░░░░░░░░██────#
    #─────████████████████─██████████████─████████──────████████─████████████████────#
    #────────────────────────────────────────────────────────────────────────────────#
    #********************************************************************************#
    #***************** Please donate to help improve the hard work ♥ ****************#
    #********************************************************************************#
    #**** BUSD/BCOIN/ETH/BNB (BEP20): 0xf1e43519fca44d9308f889baf99531ed0de903fc ****#
    #**** PayPal: https://www.paypal.com/donate/?hosted_button_id=82CABN6CYVG6U *****#
    #************* Nubank: https://nubank.com.br/pagar/1jxcl/z5fyuL6S28 *************#
    #****************** Pix: 42a762ed-e6ec-4059-a88e-f168b9fbc63f *******************#
    #********************************************************************************#    
    """

    print(hello_world)
            
    # Initialize pyautogui library
    await asyncio.create_task(initialize_pyautogui())

    # Delete old log files
    await asyncio.create_task(delete_log_files())

    # Delete old folders
    await asyncio.create_task(delete_folders())

    # Countdown timer before start the bot
    await asyncio.create_task(countdown_timer())

    logger.info('------------------- New Execution ----------------\n')
    logger.info('Donate on BUSD/BCOIN/ETH/BNB (BEP20): 0xf1e43519fca44d9308f889baf99531ed0de903fc')
    logger.info('Donate on PayPal: https://www.paypal.com/donate/?hosted_button_id=82CABN6CYVG6U')
    logger.info('Donate on Nubank: https://nubank.com.br/pagar/1jxcl/z5fyuL6S28')
    logger.info('Donate on Pix: 42a762ed-e6ec-4059-a88e-f168b9fbc63f')
    logger.info('Starting Bot..... Bot started!')

    if refresh_heroes_only != False:
        logger.info('The "refresh heroes only" option is enable, so only the refresh will work on the bot. If you want bot working the whole process, close the bot and change the option to False!')

    if refresh_heroes_time == work_heroes_time:
        logger.critical('You should set a different time for "refresh_heroes_time" and also send them to work from "work_heroes_time". Otherwise these steps might not start correctly.')

    # Create a scheduler for certain functions
    scheduler = BackgroundScheduler(timezone=str(tzlocal.get_localzone()))
    trigger = SetTrigger()

    if (refresh_heroes_time*60) > 59:
        logger.info('Scheduling the refresh heroes positions every %s minute(s)!' % (refresh_heroes_time))
        # - Do a full review on games        
        scheduler.add_job(trigger.UpdateSetRefresh, 'interval', seconds=(refresh_heroes_time*60), id='1', name='refresh_hereoes_positions', misfire_grace_time=180)

    if refresh_heroes_only != True:
        if (work_heroes_time*60) > 59:
            logger.info('Scheduling the time for heroes to work every %s minute(s)!' % (work_heroes_time))
            # - Send heroes to work
            scheduler.add_job(trigger.UpdateSetWork, 'interval', seconds=(work_heroes_time*60), id='2', name='send_heroes_to_work', misfire_grace_time=300)

        if (refresh_browser_time*60) > 59:
            logger.info('Scheduling the time for refreshing the browser every %s minute(s)!' % (refresh_browser_time))
            # - Do a full review on games        
            scheduler.add_job(trigger.UpdateSetReload, 'interval', seconds=(refresh_browser_time*60), id='3', name='refresh_browser_time', misfire_grace_time=180)

    if len(scheduler.get_jobs()) > 0:
        scheduler.start()

    applications, website_browser = get_browser()
    logger.info('Number of accounts that the bot will run: %s' % (len(applications)))
    
    if 'Bombcrypto' not in website_browser:
        logger.error('Bombcrypto website not open yet, please open the browser before starting this bot! Exiting bot...')
        os._exit(0)
    else:
        if len(applications) > 0:            
            # Iterate through applications *once*, starting the app and creating the related bot name for future use.
            for app in applications:
                if enable_multiaccount != False:
                    print('Going to bot: ' + str(app[1]))
                    browser = Desktop(backend="uia").windows(title=app[0])[0]
                    browser.set_focus()
                    app.append(browser)
                await asyncio.create_task(first_start(app_name=app[1]))                

            i = 0
            j = 0
            k = 0
            # Cycle through the bots in one loop rather than restarting the loop in an infinite loop
            for app in cycle(applications):
                if enable_multiaccount != False and refresh_heroes_only != True:
                    print('Going to bot: ' + str(app[1]))
                    app[2].set_focus()
                if refresh_heroes_only != False:
                    if trigger.set_refresh != False:
                        if enable_multiaccount != False:
                            print('Going to bot: ' + str(app[1]))
                            app[2].set_focus()
                        await asyncio.create_task(refresh_hereoes_positions(app_name=app[1]))
                        i += 1
                    if i == len(applications) and trigger.set_refresh != False:
                        i = 0
                        trigger.set_refresh = False
                if refresh_heroes_only != True:                
                    # Steps of this bot:
                    # - Login Metamask
                    await asyncio.create_task(login_metamask(app_name=app[1]))                    
                    # - Connect Wallet on BomberCypto game                       
                    await asyncio.create_task(connect_wallet(app_name=app[1]))
                    # - Login Metamask
                    await asyncio.create_task(login_metamask(app_name=app[1]))
                    # - Treasure Hunt game mode
                    await asyncio.create_task(treasure_hunt_game(refresh_only=True, app_name=app[1]))   
                    # - New map feature
                    await asyncio.create_task(new_map(app_name=app[1]))
                    # - Check for errors on game
                    await asyncio.create_task(skip_error_on_game(app_name=app[1]))

                    # - Time to call some functions
                    if trigger.set_refresh != False:
                        await asyncio.create_task(refresh_hereoes_positions(app_name=app[1]))
                        i += 1
                    if trigger.set_work != False:
                        await asyncio.create_task(send_heroes_to_work(app_name=app[1]))
                        j += 1
                    if trigger.set_reload != False:
                        await asyncio.create_task(reload_page(app_name=app[1]))
                        k += 1
                    if i == len(applications) and trigger.set_refresh != False:
                        i = 0
                        trigger.set_refresh = False
                    elif j == len(applications) and trigger.set_work != False:
                        j = 0
                        trigger.set_work = False
                    elif k == len(applications) and trigger.set_reload != False:
                        k = 0
                        trigger.set_reload = False
                                        
        else:
            logger.error('No account/profile found in the config.yaml file or profile do not match with profile opened, please check and restart the bot. Exiting bot...')
            os._exit(0)

if __name__ == "__main__":
    try:                
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()
    except Exception as e:
        print("Exception: " + str(e))
        exit()