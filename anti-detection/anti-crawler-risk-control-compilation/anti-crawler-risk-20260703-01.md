# 行为分析篇：如何模拟人类行为，避免行为模型检测？

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2026-07-03
> 归档日期: 2026-07-13
> 分类: anti-detection
>
> 指纹伪装得再好，行为模式不对依然会被风控揪出来。现代反爬系统（如 Datadome、Akamai Bot Manager、Cloudflare Bot > Management）已经把用户行为建模做到了毫秒级： > 你鼠标怎么动、键盘怎么敲、页面怎么滚、两次操作间隔多少、甚至屏幕有没有晃动，都在实时打分。 。

> 指纹伪装得再好，行为模式不对依然会被风控揪出来。现代反爬系统（如 Datadome、Akamai Bot Manager、Cloudflare Bot
> Management）已经把用户行为建模做到了毫秒级：  **
> 你鼠标怎么动、键盘怎么敲、页面怎么滚、两次操作间隔多少、甚至屏幕有没有晃动，都在实时打分。  **

这一篇不讲理论，直接给  ** 可执行的模拟策略和代码  ** 。目标是让你的自动化脚本在行为层面看起来像真人。


##  一、人类行为的核心特征

风控建模通常关注这几个维度：

维度  |  人类特征  |  自动化常见错误
---|---|---
** 鼠标移动  ** |  曲线路径、加速度、微抖动、非直线  |  直线、匀速、完美贝塞尔
** 点击  ** |  有停留、有偏移、双击频率低  |  瞬间点击、坐标精确
** 滚动  ** |  变速、随机停顿、偶尔反向  |  匀速、一次性滚到底
** 键盘输入  ** |  间隔不等、有错字再修正  |  固定间隔、无错误
** 页面停留  ** |  阅读时间分布广、有回头  |  极短或完全一致
** 视口变化  ** |  窗口大小调整、焦点切换  |  固定不变
** 并发  ** |  单线程、串行操作  |  并行大量请求

** 核心原则：增加熵，减少规律性。  **


##  二、鼠标移动模拟


###  2.1 人类鼠标轨迹的特征

  * ** 起点到终点不是直线  ** ：有弧线、有抖动

  * ** 速度变化  ** ：先加速后减速（起始快、接近目标慢）

  * ** 有微小过冲  ** ：超过目标然后回拉

  * ** 轨迹受重力影响  ** ：水平移动比垂直移动更自然（人手腕左右移动更方便）

###  2.2 用 Bezier 曲线模拟鼠标移动（Python + PyAutoGUI）

  *


    pip install pyautogui numpy


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import pyautoguiimport numpy as npimport randomimport timedef bezier_curve(start, end, control_points=None, steps=50):    """    生成贝塞尔曲线上的点序列    start, end: (x, y)    control_points: list of (x, y)，默认生成两个随机控制点    steps: 路径点数    """    if control_points is None:        # 生成两个随机控制点，使路径弯曲        dx = end[0] - start[0]        dy = end[1] - start[1]        dist = np.hypot(dx, dy)        offset_x = random.uniform(-dist*0.2, dist*0.2)        offset_y = random.uniform(-dist*0.2, dist*0.2)        cp1 = (start[0] + dx*0.25 + offset_x, start[1] + dy*0.25 + offset_y)        cp2 = (start[0] + dx*0.75 + offset_x, start[1] + dy*0.75 + offset_y)        control_points = [cp1, cp2]    points = []    for t in np.linspace(0, 1, steps):        # 三次贝塞尔公式        x = (1-t)**3 * start[0] + 3*(1-t)**2*t * control_points[0][0] + 3*(1-t)*t**2 * control_points[1][0] + t**3 * end[0]        y = (1-t)**3 * start[1] + 3*(1-t)**2*t * control_points[0][1] + 3*(1-t)*t**2 * control_points[1][1] + t**3 * end[1]        points.append((int(x), int(y)))    return pointsdef human_move_mouse(target_x, target_y, duration_range=(0.3, 1.2)):    """    模拟人类鼠标移动到目标位置    duration_range: 总移动时间范围（秒）    """    current_x, current_y = pyautogui.position()    start = (current_x, current_y)    end = (target_x, target_y)    # 生成路径    path = bezier_curve(start, end, steps=random.randint(30, 80))    # 计算每个点的延迟（模拟加速度）    total_time = random.uniform(*duration_range)    delays = _generate_accelerated_delays(len(path), total_time)    for point, delay in zip(path, delays):        pyautogui.moveTo(point[0], point[1], duration=0)  # 立即移动        time.sleep(delay)    # 最后加一点微抖动（模拟手抖）    for _ in range(random.randint(0, 3)):        jitter_x = random.randint(-2, 2)        jitter_y = random.randint(-2, 2)        pyautogui.moveRel(jitter_x, jitter_y, duration=0.01)        time.sleep(0.02)def _generate_accelerated_delays(num_points, total_time):    """    生成符合先快后慢（接近目标时减速）的延迟序列    """    # 使用二次函数分布：前半段快，后半段慢    t = np.linspace(0, 1, num_points)    weights = 1 + t**2 * 3  # 越往后权重越大（越慢）    weights = weights / weights.sum()    delays = weights * total_time    return delays.tolist()# 使用示例human_move_mouse(800, 600)


###  2.3 点击模拟

  *   *   *   *   *   *   *   *   *   *   *   *   *   *


    def human_click(x=None, y=None, button='left'):    """模拟人类点击：先移动、停顿、点击、释放"""    if x is not None and y is not None:        human_move_mouse(x, y)    # 随机停顿 0.1~0.4 秒（假装在考虑）    time.sleep(random.uniform(0.1, 0.4))    pyautogui.mouseDown(button=button)    time.sleep(random.uniform(0.05, 0.15))  # 按下持续时间    pyautogui.mouseUp(button=button)    # 点击后稍微移动（防止连续点击同一位置）    time.sleep(random.uniform(0.05, 0.2))    pyautogui.moveRel(random.randint(-3, 3), random.randint(-3, 3), duration=0.05)# 使用human_click(500, 400)


##  三、键盘输入模拟

###  3.1 人类打字特征

  * ** 击键间隔不均匀  ** ：字母间 100-300ms，空格和标点更长

  * ** 有时打错并删除重打  **

  * ** 组合键（Ctrl+C）不会逐字输入  **

  * ** 长文本中有短暂停顿  **

###  3.2 模拟打字（Python + pynput）

  *


    pip install pynput


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import randomimport timefrom pynput.keyboard import Controller, Keykeyboard = Controller()# 定义常见英文键的延迟分布（单位秒）KEY_DELAY_MAP = {    'default': (0.08, 0.20),      # 普通字母    'space': (0.15, 0.40),    'enter': (0.20, 0.60),    'shift': (0.10, 0.30),    'backspace': (0.12, 0.28),}def human_type(text, error_rate=0.03):    """    模拟人类打字，支持随机错误和修正    error_rate: 出错概率（0~1）    """    for char in text:        # 随机决定是否打错        if random.random() < error_rate:            # 打一个错误字符            wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')            keyboard.press(wrong_char)            time.sleep(random.uniform(0.05, 0.15))            keyboard.release(wrong_char)            # 停顿后删除            time.sleep(random.uniform(0.2, 0.5))            keyboard.press(Key.backspace)            time.sleep(random.uniform(0.05, 0.12))            keyboard.release(Key.backspace)            # 重新打正确字符            time.sleep(random.uniform(0.1, 0.3))        # 正常输入        if char == ' ':            delay_range = KEY_DELAY_MAP['space']        elif char == '\n':            delay_range = KEY_DELAY_MAP['enter']        else:            delay_range = KEY_DELAY_MAP['default']        keyboard.press(char)        time.sleep(random.uniform(*delay_range))        keyboard.release(char)        # 偶尔长停顿（模拟思考）        if random.random() < 0.005:  # 0.5% 概率            time.sleep(random.uniform(0.8, 2.0))# 使用human_type("Hello, this is a test message.", error_rate=0.04)


##  四、页面滚动模拟

###  4.1 人类滚动特点

  * ** 不是匀速  ** ：开始时加速，中间匀速，结束前减速

  * ** 偶尔停顿  ** ：阅读内容时会停

  * ** 可能反向滚动  ** ：回头看上面内容

  * ** 滚动距离随机  ** ：不会每次固定像素

###  4.2 用 JavaScript 在浏览器中模拟（Playwright）

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import asyncioimport randomfrom playwright.async_api import async_playwrightasync def human_scroll(page, scroll_distance=None, scroll_pause_range=(1.0, 3.0)):    """    模拟人类滚动页面    scroll_distance: 总滚动距离（像素），None则随机    scroll_pause_range: 每次滚动后的暂停范围（秒）    """    if scroll_distance is None:        # 获取页面高度，随机滚动一部分        body_height = await page.evaluate('document.body.scrollHeight')        scroll_distance = random.randint(int(body_height * 0.3), int(body_height * 0.8))    # 分多次滚动，每次距离随机    remaining = scroll_distance    while remaining > 0:        step = random.randint(100, min(400, remaining))        remaining -= step        # 平滑滚动（使用 CSS smooth scroll）        await page.evaluate(f'''            window.scrollBy({{                top: {step},                behavior: 'smooth'            }});        ''')        # 等待滚动完成        await asyncio.sleep(random.uniform(0.3, 0.8))        # 暂停阅读        pause_time = random.uniform(*scroll_pause_range)        await asyncio.sleep(pause_time)        # 偶尔往回滚一点（假装看漏了）        if random.random() < 0.15:            back_step = random.randint(30, 150)            await page.evaluate(f'window.scrollBy({{top: {-back_step}, behavior: "smooth"}})')            await asyncio.sleep(random.uniform(0.5, 1.5))    # 最终停在某个位置，不完全到底部    final_offset = random.randint(-200, -50)    await page.evaluate(f'window.scrollBy({{top: {final_offset}, behavior: "smooth"}})')# 使用async def main():    async with async_playwright() as p:        browser = await p.chromium.launch(headless=False)        page = await browser.new_page()        await page.goto('https://example.com/long-page')        await human_scroll(page)        await browser.close()asyncio.run(main())


##  五、时间间隔与节奏控制

###  5.1 人类操作的时间分布

  * ** 两次操作间隔  ** ：通常在 0.5~5 秒之间，呈长尾分布

  * ** 页面加载后  ** ：有 1~3 秒的"阅读"时间

  * ** 表单填写  ** ：每个字段之间有 0.5~2 秒停顿

  * ** 提交前  ** ：有 0.3~1 秒的"确认"停顿

###  5.2 生成符合分布的延迟

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import randomimport numpy as npdef human_delay(mean=1.5, std=0.8, min_val=0.2, max_val=5.0):    """    生成符合截断正态分布的人类延迟（秒）    """    delay = np.random.normal(mean, std)    delay = max(min_val, min(max_val, delay))    return delaydef wait_between_actions(action_type='generic'):    """根据不同操作类型返回合适的等待时间"""    config = {        'page_load': (1.5, 0.8, 0.5, 4.0),       # 页面加载后阅读        'field_fill': (0.8, 0.5, 0.2, 3.0),      # 填完一个字段        'click': (0.6, 0.4, 0.1, 2.0),           # 点击后等待        'scroll': (2.0, 1.0, 0.5, 6.0),          # 滚动后阅读        'submit': (0.5, 0.3, 0.1, 1.5),          # 提交前确认    }    mean, std, min_v, max_v = config.get(action_type, (1.0, 0.5, 0.2, 3.0))    return human_delay(mean, std, min_v, max_v)# 使用time.sleep(wait_between_actions('field_fill'))


##  六、高级技巧：鼠标轨迹记录与回放

对于高安全场景（如银行、支付），可以用  ** 真人的鼠标轨迹录下来，然后回放  ** 。这样行为模型几乎无法区分。

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    # 录制鼠标轨迹（简化版）import pyautoguiimport jsonimport timedef record_mouse_trajectory(seconds=10):    """录制一段时间内的鼠标位置"""    trajectory = []    start_time = time.time()    while time.time() - start_time < seconds:        x, y = pyautogui.position()        timestamp = time.time() - start_time        trajectory.append({"x": x, "y": y, "t": timestamp})        time.sleep(0.01)  # 约 100Hz 采样    return trajectory# 保存到文件traj = record_mouse_trajectory(5)with open("mouse_traj.json", "w") as f:    json.dump(traj, f)# 回放def replay_trajectory(file_path):    with open(file_path) as f:        traj = json.load(f)    start_time = time.time()    for point in traj:        elapsed = time.time() - start_time        if point['t'] > elapsed:            time.sleep(point['t'] - elapsed)        pyautogui.moveTo(point['x'], point['y'])


##  七、综合示例：模拟真实用户会话

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import asyncioimport randomfrom playwright.async_api import async_playwrightfrom human_behaviors import human_scroll, human_type, human_click  # 假设封装async def simulate_user_session(url, form_data):    async with async_playwright() as p:        browser = await p.chromium.launch(headless=False)        context = await browser.new_context(            viewport={'width': 1366, 'height': 768},            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...'        )        page = await context.new_page()        # 1. 打开页面        await page.goto(url, wait_until='networkidle')        await asyncio.sleep(human_delay(2.0, 1.0, 1.0, 4.0))        # 2. 滚动页面（假装浏览）        await human_scroll(page, scroll_pause_range=(1.0, 3.0))        # 3. 找到输入框并点击        input_selector = '#username'        await page.wait_for_selector(input_selector)        box = await page.locator(input_selector).bounding_box()        await human_click(box['x'] + box['width']/2, box['y'] + box['height']/2)        await asyncio.sleep(human_delay(0.3, 0.2, 0.1, 0.8))        # 4. 输入用户名（模拟打字）        await page.keyboard.type(form_data['username'], delay=0)  # 用我们自己的 type 替代        # 更真实：调用 human_type 通过 keyboard 逐字符        # 此处简化        await asyncio.sleep(human_delay('field_fill'))        # 5. 填写密码        # ... 类似        # 6. 点击提交按钮        submit_btn = await page.query_selector('#submit-btn')        btn_box = await submit_btn.bounding_box()        await human_click(btn_box['x'] + btn_box['width']/2, btn_box['y'] + btn_box['height']/2)        # 7. 等待结果        await page.wait_for_timeout(3000)        await browser.close()


##  八、风控行为检测的常见陷阱与对策

风控检测点  |  自动化常见错误  |  正确做法
---|---|---
** 鼠标移动速度过快  ** |  瞬间跳到目标  |  使用贝塞尔曲线 + 加速度
** 点击坐标完全精确  ** |  总是元素中心  |  随机偏移 ±3~10px
** 无鼠标移动直接点击  ** |  ` element.click()  ` 无轨迹  |  先移动再点击
** 滚动匀速  ** |  ` window.scrollTo  ` 一次性  |  分段平滑滚动 + 随机停顿
** 键盘输入间隔固定  ** |  ` send_keys  ` 每字符相同延迟  |  不等间隔 + 偶尔错误
** 无页面交互前就提交  ** |  打开即填表  |  先滚动、悬停、阅读
** 所有操作时间完美  ** |  无长停顿  |  加入思考/阅读时间
** 窗口始终聚焦  ** |  从不切换标签页  |  偶尔切换窗口（可选）


##  九、注意事项

  1. ** 不要过度模拟  ** ：太完美的"人类"反而可疑。保留一些不规则性，但不要刻意制造太多异常。

  2. ** 结合指纹伪装  ** ：行为模拟要和 TLS/HTTP2 指纹、浏览器指纹一起工作，单一维度突破不了强风控。

  3. ** 测试验证  ** ：用  ` https://bot.sannysoft.com/  ` 或  ` https://fingerprintjs.com/demo  ` 检查你的自动化是否被检测。

  4. ** 合规优先  ** ：本文技术仅用于学习、测试自己系统的安全性。未经授权模拟他人网站用户行为可能违反 ToS 和法律。


行为模拟是猫鼠游戏中最耗精力的部分。  ** 没有银弹，只有持续优化  **
。建议记录每次被拦截的场景，针对性调整参数。如果你有具体被检测的行为（比如鼠标轨迹被识别），欢迎继续交流。
