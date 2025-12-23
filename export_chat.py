# 导出账号所有联系人和群组的id,以便于在其他账号重新添加
# 启动后, 提示Please enter your phone (or bot token): 直接输入你的手机号,必须带上国家区号,如+8613800001234
# 输入验证码,你的手机或电脑上的 Telegram App(官方客户端)会收到一条来自 "Telegram" 的官方服务消息,里面有 5 位数验证码,输入后回车
# 一旦验证通过，脚本就会继续执行(显示 登录成功)，并且会在目录下生成 session_old.session 文件,下次再运行脚本时,因为它检测到了这个文件,就不会再让你输入手机号了

import asyncio  # 导入 asyncio 库用于异步编程
import pandas as pd  # 引入 pandas 库
from telethon import TelegramClient  # 导入 Telethon 客户端核心类
import export_config  # 导入本地配置文件


async def main():
    # 初始化旧账号的客户端实例
    # 首次运行时，会在终端提示输入旧账号的手机号和验证码
    client = TelegramClient(export_config.SESSION_OLD, export_config.API_ID, export_config.API_HASH)

    print(f"🚀 正在启动旧账号 ({export_config.SESSION_OLD})...")  # 打印启动日志
    # await client.start()  # 建立连接并登录, 用 async with 代替
    async with client:
        me = await client.get_me()  # 获取当前登录用户的信息
        print(f"✅ 登录成功: {me.first_name} (+{me.phone})")  # 打印登录用户信息

        dialogs_list = []  # 初始化列表用于存储对话数据
        print("📥 正在扫描所有对话...")  # 打印扫描提示

        # 遍历账号下的所有对话 (包括群组、频道、私聊)
        async for dialog in client.iter_dialogs():
            entity = dialog.entity  # 获取对话对应的实体对象

            # 过滤逻辑：我们只能迁移有 username (公开) 的实体
            # 私有群组如果没有 username，仅凭 ID 无法在另一个账号加入
            if hasattr(entity, 'username') and entity.username:

                # 判断对话类型
                chat_type = 'User'  # 默认为用户
                if entity.broadcast:  # 如果是广播频道
                    chat_type = 'Channel'
                elif entity.megagroup:  # 如果是超级群组
                    chat_type = 'Group'

                # 构建数据对象
                data = {
                    'ID': entity.id,  # ID (仅供参考)
                    'Title': dialog.name,  # 对话标题
                    'Username': entity.username,  # 用户名 (核心迁移依据)
                    'Type': chat_type  # 类型
                }
                dialogs_list.append(data)  # 添加到列表
                print(f"   - 发现: {data['title']} (@{data['username']}) [{chat_type}]")  # 打印发现的对话

        # 将结果保存到 Excel 文件
        if dialogs_list:
            # 1. 将列表转换为 Pandas DataFrame (表格对象)
            df = pd.DataFrame(dialogs_list)

            # 2. 导出为 Excel 文件 (index=False 表示不保存行号)
            df.to_excel(export_config.DATA_FILE, index=False)

            print(f"\n🎉 导出完成! 共 {len(dialogs_list)} 条数据。")
            print(f"📊 Excel 文件已生成: {export_config.DATA_FILE}")
        else:
            print("⚠️ 未找到任何可迁移的公开对话。")

    # 注意：这里不需要 client.disconnect() 了，async with 会自动处理


if __name__ == '__main__':
    asyncio.run(main())  # 运行主异步函数
