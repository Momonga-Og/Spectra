import asyncio

async def reboot_bot(bot):
    await bot.close()

def schedule_reboot(bot):
    async def reboot_task():
        while True:
            await asyncio.sleep(3)  # 3 min
            await reboot_bot(bot)

    bot.loop.create_task(reboot_task())
