import asyncio
import logging

async def reboot_bot(bot):
    logging.info("Rebooting bot")
    await bot.close()

def schedule_reboot(bot):
    async def reboot_task():
        while True:
            await asyncio.sleep(18000)  # 5 hours
            await reboot_bot(bot)

    bot.loop.create_task(reboot_task())
