# ------------------------------- 모듈 -------------------------------#
import os
import pickle

# ------------------------------- 객체 -------------------------------#

# 아이템 객체: 이름 / HP 회복량
class Item:
    def __init__(self, name: str, recovery: int):
        self.name = name
        self.recovery = recovery

# 임무 객체: 임무 이름 / 설명 / 수령 여부 / 완료 여부
class Quest:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.received = False 
        self.cleared = False   

# 장소 객체: 구매 / 판매 / 정보 / 임무 여부 / 정답 여부
class Place:
    def __init__(self, name: str, buy_menu: dict = {}, sell_menu: dict = {}, 
                info: str = "", quest_give: "Quest" = None, quest_solve: "Quest" = None, 
                answer: str = "", game_clear: bool = False):
        self.name = name
        self.buy_menu = buy_menu if buy_menu else {}
        self.sell_menu = sell_menu if sell_menu else {}
        self.info = info
        self.quest_give = quest_give
        self.quest_solve = quest_solve
        self.answer = answer
        self.game_clear = game_clear

    # 해당 장소의 상호작용 목록 확인
    def interactions(self) -> list:
        labels = []
        if self.buy_menu:
            labels.append("구매")
        if self.sell_menu:
            labels.append("판매")
        if self.quest_give or self.quest_solve or self.game_clear:
            labels.append("임무")
        return labels

    # 구매 가능 여부 확인
    def can_buy(self) -> bool:
        return bool(self.buy_menu)

    # 판매 가능 여부 확인
    def can_sell(self) -> bool:
        return bool(self.sell_menu)

    # 임무 존재 여부 확인
    def has_quest(self) -> bool:
        return self.quest_give is not None or self.quest_solve is not None

# 플레이어 객체: 체력 / 잔액 / 위치 / 가방 / 임무 - 이동 기능 포함
class Player:
    def __init__(self, hp: int, money: int, location: str, location_idx: list, 
                 bag: dict = {}, tasks: list = []):
        self.hp = hp
        self.money = money
        self.location = location
        self.location_idx = list(location_idx)
        self.bag = bag
        self.tasks = tasks

    # 가방 아이템 존재 여부 확인: check_bag에 전달
    def has_bag_items(self) -> bool:
        return bool(self.bag)

    # 가방에서 아이템 제거: sell_item에서 사용
    def clean_bag(self):
        self.bag = {k: v for k, v in self.bag.items() if v > 0}

    # 임무 진행 여부 확인: check_task에 전달
    def has_task(self) -> bool:
        return any(q.received and not q.cleared for q in self.tasks)

    # 임무 수령: quest_output에서 사용
    def add_task(self, quest: "Quest"):
        if quest not in self.tasks:
            self.tasks.append(quest)
        quest.received = True

    # 이동 기능: check_move 함수로 이동 가능 여부를 확인 후 이동 및 반영
    def move(self, direction: str, school_map: list, difficulty: str) -> str:
        directions = {"북": (0, 1), "남": (0, -1), "동": (1, 1), "서": (1, -1),}
        fatigue = {"보통": 1, "어려움": 2}
        
        if direction not in directions:
            return "잘못된 입력입니다."

        idx, num = directions[direction]
        if not self.check_move(school_map, idx, num):
            return "그 방향은 막혔어."

        self.hp -= fatigue.get(difficulty, 1)
        self.location_idx[idx] += num
        self.location = school_map[self.location_idx[0]][self.location_idx[1]]
        return f"{self.location}(으)로 이동했습니다."

    # 이동 가능 여부 확인 함수: move 함수에 전달
    def check_move(self, school_map: list, axis_idx: int, delta: int) -> bool:
        after = self.location_idx.copy()
        after[axis_idx] += delta
        if after[0] < 0 or after[1] < 0:
            return False
        try:
            cell = school_map[after[0]][after[1]]
        except IndexError:
            return False
        return cell is not None

    # 상태 출력: 
    def print_status(self, school_map: list, ui_mode: str) -> list:
        # 위치가 None일 때 막힘 출력
        def adjust_dirstr(v):
            return v if v is not None else "막힘"

        r, c = self.location_idx[0], self.location_idx[1]
        east = school_map[r][c + 1] if c + 1 < len(school_map[r]) else None
        west = school_map[r][c - 1] if c - 1 >= 0 else None
        south = school_map[r - 1][c] if r - 1 >= 0 else None
        north = school_map[r + 1][c] if r + 1 < len(school_map) else None

        if ui_mode == "minimal":
            return [
                f"계좌의 잔액 = {self.money:,}원",
                f"HP = {self.hp}",
                f"현재위치 = {self.location}",
                f"동서남북 = {adjust_dirstr(east)}, {adjust_dirstr(west)}, {adjust_dirstr(south)}, {adjust_dirstr(north)}",
            ]
        
        else:
            return [
                "< 상태창 >",
                f"1. 소지금: {self.money}원",
                f"2. 체력:   {self.hp}",
                f"3. 위치: {self.location}",
                f"4. 동쪽위치: {adjust_dirstr(east)}",
                f"5. 서쪽위치: {adjust_dirstr(west)}",
                f"6. 남쪽위치: {adjust_dirstr(south)}",
                f"7. 북쪽위치: {adjust_dirstr(north)}",
            ]

# ------------------------- I/O 로깅 / 카운터 -------------------------#
io_counter = 0
input_log = []

# 텍스트 출력 함수: minimal일 때 [N] 추가
def game_output(text: str = ""):
    global io_counter
    io_counter += 1
    if settings["ui_mode"] == "minimal":
        lines = text.split("\n") if text else [""]
        print(f"[{io_counter}] {lines[0]}")
        for line in lines[1:]:
            print(line)
    else:
        print(text)


# 리스트를 받아 이를 텍스트 출력 함수로 보내는 기능
def game_output_block(texts: list):
    cleaned = [t for t in texts if t not in ("", None)]
    output_text("\n".join(cleaned))


# 텍스트 입력 함수: minimal일 때 [N] 추가
def game_input(prompt: str = "> ") -> str:
    global io_counter
    io_counter += 1
    if settings["ui_mode"] == "minimal":
        user_input = input(f"[{io_counter}] {prompt}")
    else:
        user_input = input(prompt)
    input_log.append(user_input)
    return user_input


# ---------------------------- UI 분리  ----------------------------#

# 기본 화면 출력
def render_main(message: str):
    if settings["ui_mode"] == "full":
        main_output(message)
    else:
        game_output(message)


# 특수 화면 출력(가방, 상태출력, 임무 등)
def render_panel(texts: list, message: str):
    if settings["ui_mode"] == "full":
        common_output(texts, message)
    else:
        block = texts
        block.append(message)
        game_output_block(block)


# ---------------------------- 기초 출력 -----------------------------#

# 초기 출력 : UI 모드 선택 → 게임 설명 및 난이도 설정
def uiselect_output():
    while True:
        game_output(
            "보조 인터페이스를 사용하시겠습니까?\n"
            "1) 사용 O - 박스, 지도 그림, 상태 패널 등을 화면에 표시\n"
            "2) 사용 X - 텍스트만 [번호] 와 함께 표시"
        )
        choice = game_input()
        if choice == "1":
            settings["ui_mode"] = "full"
            return
        elif choice == "2":
            settings["ui_mode"] = "minimal"
            return
        else:
            game_output("잘못된 입력입니다.")


# 초기 출력 : 게임 설명 및 난이도 설정
def initial_output(texts: list, message: str, width: int = 73, height: int = 13):
    prepGame = True
    difficulty = ["보통", "어려움"]
    while prepGame:
        prepGame = False
        if settings["ui_mode"] == "full":
            print("=" * width)
            print(f"[↑] 해당 게임은 화살표 위에 있는 === 줄에")
            print(f"    터미널 사이즈를 맞추는 것을 추천드립니다.")
            print("=" * width)
            for text in texts:
                print(text)
            for _ in range(max(0, height - len(texts))):
                print()
            print("=" * width)
            print(message)
            print("=" * width)
            user_input = input("> ").strip()
        else:
            # minimal 모드: 안내 한 줄 + 입력
            game_output("난이도를 선택하세요. (1: 보통 | 2: 어려움)")
            user_input = game_input()

        if user_input == "1" or user_input == "보통":
            settings["difficulty"] = difficulty[0]
        elif user_input == "2" or user_input == "어려움":
            settings["difficulty"] = difficulty[1]
        else:
            message = "잘못된 입력입니다."
            if settings["ui_mode"] == "minimal":
                game_output(message)
            prepGame = True


# 범용 출력 : 특수 출력에 사용되는 공통 출력 양식
def common_output(texts: list, message: str, width: int = 73, height: int = 13):
    print("=" * width)
    print(f"[위치]: {player.location}")
    print(f"[HP]: {player.hp}")
    print("=" * width)
    for text in texts:
        print(text)
    for _ in range(max(0, height - len(texts))):
        print()
    print("=" * width)
    print(message)
    print("=" * width)


# 기본 출력 : 게임의 기본 화면
def main_output(message: str, col: int = 6, row: int = 7):
    cell_w = 11
    h_line = "+" + (("-" * cell_w + "+") * col)
    eq_line = "=" * (cell_w * col + col + 1)
    lines = []
    loc_idx = player.location_idx
    print(eq_line)
    print(f"[위치]: {player.location}")
    print(f"[HP]: {player.hp}")
    for r in range(row - 1, -1, -1):
        if r == row - 1:
            lines.append(eq_line)
        else:
            lines.append(h_line)
        row_str = "|"
        for c in range(col):
            if r == loc_idx[0] and c == loc_idx[1]:
                cell = "★".center(cell_w)
            elif schoolMap[r][c] is None:
                cell = "|" * cell_w
            else:
                cell = "·".center(cell_w)
            row_str += cell + "|"
        lines.append(row_str)
    lines.append(eq_line)
    print("\n".join(lines))
    print(message)
    print(eq_line)
    cell_w = 11
    h_line = "+" + (("-" * cell_w + "+") * col)
    eq_line = "=" * (cell_w * col + col + 1)
    lines = []
    print(eq_line)
    print(f"[위치]: {location}")
    print(f"[HP]: {char_stat['hp']}")
    for r in range(row - 1, -1, -1):
        if r == row - 1:
            lines.append(eq_line)
        else:
            lines.append(h_line)
        row_str = "|"
        for c in range(col):
            if r == loc_idx[0] and c == loc_idx[1]:
                cell = "★".center(cell_w)
            elif schoolMap[r][c] is None:
                cell = "|" * cell_w
            else:
                cell = "·".center(cell_w)
            row_str += cell + "|"
        lines.append(row_str)
    lines.append(eq_line)
    print("\n".join(lines))
    print(message)
    print(eq_line)


# ---------------------------- 기능 출력 -----------------------------#

# 도움말 출력
def help_output(texts: list, message: str):
    if settings["ui_mode"] == "minimal":
        game_output_block(texts)
        return

    while True:
        render_panel(texts, message)
        user_input = game_input().strip()
        if user_input == "닫기":
            render_main("게임조작법창을 닫았습니다.")
            break
        else:
            message = "잘못된 입력입니다. (닫기: 종료)"


# 상태 출력 : 상태창 출력
def status_output(texts: list, message: str):
    if settings["ui_mode"] == "minimal":
        game_output_block(texts)
        return

    while True:
        render_panel(texts, message)
        user_input = game_input().strip()
        if user_input == "닫기":
            render_main("상태창을 닫았습니다.")
            break
        else:
            message = "잘못된 입력입니다. (닫기: 종료)"


# 가방 출력 : 가방 출력 및 아이템 사용
def bag_output(texts: list, message: str):
    while True:
        render_panel(texts, message)
        user_input = game_input().strip()
        if user_input == "닫기":
            render_main("가방을 닫았습니다.")
            break
        else:
            useItem = use_item(user_input)
            if check_bag():
                texts = open_bag()
                message = useItem
            else:
                render_main(useItem)
                break


# 임무 출력 : 현재 사용자의 임무 출력
def task_output(texts: list, message: str):
    if settings["ui_mode"] == "minimal":
        game_output_block(texts)
        return

    while True:
        render_panel(texts, message)
        user_input = game_input().strip()
        if user_input == "닫기":
            render_main("임무창을 닫았습니다.")
            break
        else:
            message = "잘못된 입력입니다. (닫기: 종료)"


    while True:
        common_output(texts, message)
        user_input = input("> ")
        if user_input == "q":
            main_output("임무창을 닫았습니다.", location_idx)
            break
        else:
            message = "잘못된 입력입니다."


# 불러오기 출력 : 저장된 파일 목록 출력 및 불러오기
def load_output(save_dir: str, message: str):
    save_dir_ = save_dir
    texts = load_game_list(save_dir)[0]
    dir_list = load_game_list(save_dir)[1]
    change_dir = False
    while True:
        render_panel(texts, message)

        if change_dir:
            save_dir = game_input().strip()
            if check_load_empty(save_dir):
                message = "잘못된 입력입니다."
                save_dir = save_dir_
            else:
                texts = load_game_list(save_dir)[0]
                dir_list = load_game_list(save_dir)[1]
                message = f"{os.path.basename(save_dir)}(으)로 폴더를 변경했습니다."
                save_dir_ = save_dir
            change_dir = False
            continue
        else:
            user_input = game_input().strip()

        if user_input == "닫기":
            render_main("불러오기를 종료합니다.")
            break
        elif user_input == "0":
            change_dir = True
            message = "변경할 폴더를 입력하세요."
        elif user_input.isdigit() and 1 <= int(user_input) <= len(dir_list):
            file_name = dir_list[int(user_input) - 1]
            message = load_game(save_dir, file_name)
            render_main(message)
            break
        else:
            message = "잘못된 입력입니다. (닫기: 종료 | 0: 폴더 변경)"


# 구매 출력 : 상점 출력 및 아이템 구매
def buy_output(texts: list, message: str, location_name: str):
    place = places.get(location_name)
    if place is None or not place.can_buy():
        render_main("이 장소에서는 구매할 수 없습니다.")
        return

    # buy_menu: {Item 객체: 가격}
    while True:
        render_panel(texts, message)
        user_input = game_input().strip()

        if user_input == "닫기":
            render_main("상점 이용을 종료합니다.")
            break

        # 입력에서 어떤 Item 을 가리키는지 결정
        menu_items = list(place.buy_menu.items())  # [(Item, price), ...]
        target_item = None
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(menu_items):
                target_item = menu_items[idx][0]
            else:
                message = "잘못된 입력입니다."
                continue
        else:
            # 이름으로 매칭
            for item, _ in menu_items:
                if item.name == user_input:
                    target_item = item
                    break
            if target_item is None:
                message = "잘못된 입력입니다."
                continue

        price = place.buy_menu[target_item]
        if player.money >= price:
            player.money -= price
            player.bag[target_item.name] = player.bag.get(target_item.name, 0) + 1
            message = f"→ {target_item.name} 구매 완료 (잔액: {player.money}원)"
            texts = show_shop(location_name)
        else:
            message = f"돈이 부족합니다. (필요: {price}원, 보유: {player.money}원)"


# 판매 출력 : 상점 출력 및 아이템 판매
def sell_output(texts: list, message: str, location_name: str):
    pass


# ---------------------------- 기타 출력 -----------------------------#

# 도움말 출력 리스트
def print_help():
    printHelp = []
    printHelp.append("< 게임 조작법 >")
    printHelp.append(f"[w/s/a/d]: 상하좌우로 이동")
    printHelp.append(f"[p]: 현재 장소의 구매창 열기")
    printHelp.append(f"[o]: 현재 장소의 판매창 열기")
    printHelp.append(f"[f]: 임무 상호작용하기")
    printHelp.append(f"[b]: 가방 확인 및 아이템 사용")
    printHelp.append(f"[t]: 임무 확인")
    printHelp.append(f"[v]: 현재 상태 확인")
    printHelp.append(f"[h]: 도움말 확인")
    printHelp.append(f"[1/2]: 게임 저장하기/불러오기")
    return printHelp


# 난이도 출력 리스트
def print_setdifficulty():
    printSetdifficulty = []
    printSetdifficulty.append("")
    printSetdifficulty.append("< 난이도 설정 >")
    printSetdifficulty.append(f"1. 보통 | 2. 어려움")
    return printSetdifficulty


# 이동 후 상호작용 가능 장소 도착 시 표시
def show_interaction(location_name: str) -> str:
    place = places.get(location_name)
    if place is None:
        return ""
    labels = place.interactions()
    if not labels:
        return ""
    return "[" + ", ".join(labels) + "]"


# ---------------------------- 가방 함수 -----------------------------#


# 가방 확인 : T/F 반환
def check_bag():
    if char_stat["bag"]:
        return True
    else:
        return False


# 가방 열기 : 아이템 이름 및 특성 출력
def open_bag():
    openBag = []
    openBag.append("< 가방 >")
    for i, (name, count) in enumerate(char_stat["bag"].items(), 1):
        hp_recover = item_dict[name][1]
        openBag.append(f"  {i}. {name}  x{count}  (HP +{hp_recover})")
    return openBag


# 아이템 사용 : idx 기반 및 이름 기반 처리
def use_item(user_input: str):
    items = list(char_stat["bag"].items())

    if user_input.isdigit():
        idx = int(user_input) - 1
        if 0 <= idx < len(items):
            name = items[idx][0]
        else:
            return "없는 번호입니다."
    elif user_input in char_stat["bag"]:
        name = user_input
    else:
        return "가방에 없는 아이템입니다."

    recover = item_dict[name][1]
    char_stat["hp"] += recover
    char_stat["bag"][name] -= 1
    message = (
        f"→ {name}(을)를 사용했습니다. (HP +{recover}, 현재 HP: {char_stat['hp']})"
    )
    clean_inventory()
    return message


# 가방 정리 : 0개인 아이템 제거
def clean_inventory():
    char_stat["bag"] = {k: v for k, v in char_stat["bag"].items() if v != 0}


# ---------------------------- 임무 함수 -----------------------------#


# 임무 확인 : T/F 반환
def check_task():
    if char_stat["task"]:
        return True
    else:
        return False


# 임무 열기 : 임무 이름 출력 ## 진행현황 추가 예정
def open_task():
    openTask = []
    openTask.append("< 임무 >\n")
    for i, name in enumerate(char_stat["task"], 1):
        openTask.append(f"  {i}. {name}")
    return openTask


# 임무 수락 : 독수리상에서 임무 수락
def get_task():
    return


# ------------------------- 구매/판매 함수 --------------------------#


# 상호작용 : 지점 도착 시 상호작용 실행
def check_interaction(location: str, task_num: int = 0):
    if location not in interaction:
        main_output("상호작용할 것이 없습니다.", location_idx)
        return
    elif len(interaction[location]) > 1:
        task_num = interaction_output(
            show_interaction(location),
            "사용할 상호작용의 번호를 입력하세요.(q: 닫기)",
            location,
        )
        if task_num:
            task_num = int(task_num) - 1
        else:
            return
    interaction_type = interaction[location][task_num]
    if interaction_type == "상점":
        shop_output(
            show_shop(location),
            "사용할 아이템의 이름 또는 번호를 입력하세요.(q: 닫기)",
            location,
        )


# 이동 후 상호작용 가능 장소 도착 시 표시
def show_interaction(location: str):
    if location not in interaction:
        return ""
    else:
        interaction_list = []
        for interaction_type in interaction[location]:
            interaction_list.append(f"{interaction_type}")
        interaction_str = "| ".join(interaction_list)
        interaction_str = interaction_str.strip()
        interaction_str = "[" + interaction_str + "]"
        return interaction_str


# 상호작용 : 아이템 구매하기 - idx 및 이름 기반 처리
def show_shop(location: str):
    shop_list = []
    shop = ware_dict[location]
    items = list(shop.items())
    shop_list.append(f"[ {location} 상점 ] - 소지금 {char_stat['money']}원\n")
    for i, (name, stock) in enumerate(items, 1):
        price = item_dict[name][0]
        shop_list.append(f"  {i}. {name}  {price}원  (재고: {stock})")
    return shop_list


# ------------------------- 게임 저장/불러오기 --------------------------#


# 게임 저장하기 : 폴더 생성 후 각 요소 추가하기 ++ 모든 입력
def save_game():
    file_name = input("> ")
    os.makedirs("saves", exist_ok=True)
    with open(f"saves/{file_name}.txt", "w") as f:
        f.write(f"char_stat: {char_stat}\n")
        f.write(f"location: {location}\n")
        f.write(f"location_idx: {location_idx}\n")
        f.write(f"difficulty: {settings['difficulty']}\n")
    return f"{file_name}으로 저장되었습니다."


# 게임 불러오기 : 폴더에서 파일 선택 후 각 요소 불러오기 - 폴더 변경 가능
def load_game_list(save_dir: str):
    file_list = [
        f for f in os.listdir(save_dir) if not f.startswith(".") and f.endswith(".txt")
    ]
    load_list = []
    load_list.append("< 저장된 파일 목록 >")
    for i, file in enumerate(file_list):
        load_list.append(f"{i + 1}. {file}")
    return load_list, file_list


# 저장 폴더 확인 : 폴더가 없거나 파일이 없으면 True 반환
def check_load_empty(save_dir: str):
    if not os.path.isdir(save_dir):
        return True
    file_list = [
        f for f in os.listdir(save_dir) if not f.startswith(".") and f.endswith(".txt")
    ]
    if len(file_list) == 0:
        return True
    return False


# 게임 불러오기 : 파일 선택 후 각 요소 불러오기
def load_game(save_dir, file_name):
    global char_stat, location, location_idx, settings
    load_list = ["char_stat", "location", "location_idx", "difficulty"]
    with open(os.path.join(save_dir, file_name), "r") as save_file:
        for line in save_file:
            line = line.strip()
            if line.startswith(load_list[0] + ": "):
                char_stat = eval(line[len(load_list[0]) + 2 :])
            elif line.startswith(load_list[1] + ": "):
                location = line[len(load_list[1]) + 2 :]
            elif line.startswith(load_list[2] + ": "):
                location_idx = eval(line[len(load_list[2]) + 2 :])
            elif line.startswith(load_list[3] + ": "):
                settings["difficulty"] = line[len(load_list[3]) + 2 :]
    return f"{os.path.basename(file_name)}을 불러왔습니다."

# ---------------------------- 기타 함수 ----------------------------#

# 지도 생성 : 리스트 - 지도, 지도 좌표
def create_map(col: int, location: list) -> list:
    schoolMap = []
    rMap = []
    for idx, loc in enumerate(location):
        rMap.append(loc)
        if (idx + 1) % col == 0:
            schoolMap.append(rMap)
            rMap = []
    return schoolMap


# pickle 사용 임무 정보 불러오기
def load_tasks(path: str):
    with open(path, "rb") as f:
        data = pickle.load(f)

    for place_name, info_text in data["events"].items():
        if place_name in places:
            places[place_name].info = info_text
    quest_to_place = {}
    for p in places.values():
        if p.quest_solve is not None:
            quest_to_place[p.quest_solve.name] = p
    for quest_name, answer_loc in data["answers"].items():
        if quest_name in quest_to_place:
            quest_to_place[quest_name].answer = answer_loc


# ---------------------------- 변수 목록 -----------------------------#

# 학교 위치: 연대앞 버스정류장 ~ 이윤재관 (지도 raw 데이터)
school_locations = [
    "연대앞 버스정류장", "정문", "스타벅스", "세브란스병원 버스정류장", None, None,
    "공학원", "백양로1", "공터1", "암병원", "의과대학", None,
    "공학관", "백양로2", "백주년기념관", "안과병원", "제중관", None,
    "체육관", "백양로3", "공터2", "광혜원", "어린이병원", "세브란스병원",
    "중앙도서관", "독수리상", "학생회관", "루스채플", "재활병원", "치과대학",
    "백양관", "백양로5", "대강당", "음악관", "알렌관", "ABMRC",
    "종합관", "본관", "경영관", "노천극장", "새천년관", "이윤재관",
]

# 지도 생성
schoolMap = create_map(6, school_locations)

# 학교 장소 생성 - 객체 넣기
places = {}
for loc_name in school_locations:
    if loc_name is None:
        continue
    places[loc_name] = Place(loc_name)

# 아이템 정의
items = {
    "두쫀쿠": Item("두쫀쿠", recovery=10),
    "카페라떼": Item("카페라떼", recovery=5),
}

# 구매 그룹: 각 객체에 배정(장소들의 리스트, 물건 가격 dict로 이루어진 튜플)
buy_group = [
    (["학생회관"], {"두쫀쿠": 5000, "카페라떼": 3000}),
    (["스타벅스", "ABMRC"], {"두쫀쿠": 4000, "카페라떼": 2000}),
]
for names, prices in buy_group:
    for name in names:
        places[name].buy_menu = {items[item_name]: price for item_name, price in prices.items()}

# 판매 그룹: 각 객체에 배정(장소들의 리스트, 물건 가격 dict로 이루어진 튜플)
sell_group = [
    (["체육관", "공학관", "공학원", "재활병원", "어린이병원", "종합관", "노천극장"],
    {"두쫀쿠": 7000, "카페라떼": 4000},),
    (["중앙도서관", "백양관", "대강당", "백주년기념관", "안과병원", "암병원", "새천년관", "알렌관", "제중관", "의과대학", "치과대학", "세브란스병원", "본관", "경영관"],
    {"두쫀쿠": 6000, "카페라떼": 3000},),
]

for names, prices in sell_group:
    for name in names:
        places[name].sell_menu = {items[item_name]: price for item_name, price in prices.items()}

# 임무 생성
quests = {
    "정문안내": Quest(
        name="정문안내",
        description=(
            "학교에서 어떤 일들이 일어나고있는지 "
            "소식들이 모이는 독수리상에서 알아보자."
        ),
    ),
    "교내 부조리 수사": Quest(
        name="교내 부조리 수사",
        description=(
            "교내 어딘가에서 부조리가 일어나고있다. "
            "이동하고 상호작용을 해서 부조리를 찾아서 본관에 보고하라."
        ),
    ),
    "교내 위생사건 수사": Quest(
        name="교내 위생사건 수사",
        description=(
            "학생들이 단체로 식중독에 걸렸다. "
            "이동하고 상호작용을 해서 위생사건의 원인을 찾아서 세브란스에 보고하라."
        ),
    ),
}

# 기본 임무 환경 할당
places["정문"].quest_give = quests["정문안내"]
places["독수리상"].quest_give = quests["교내 부조리 수사"]
places["본관"].quest_solve = quests["교내 부조리 수사"]
places["세브란스병원"].quest_solve = quests["교내 위생사건 수사"]
places["이윤재관"].game_clear = True

# 게임 기본 설정
settings = {"difficulty": "보통", "ui_mode": "minimal"}

# 플레이어 생성
player = Player(hp=10, money=10000, location="연대앞 버스정류장", location_idx=[0, 0])

# 기본 임무 로드
load_tasks("event.bin")

# ---------------------------- 메인 함수 -----------------------------#
if __name__ == "__main__":
    initial_output(print_help() + print_setdifficulty(), "난이도를 입력하면 게임이 시작됩니다.")
    main_output("송도 생활을 마치고 신촌에 처음 도착했다. 연대앞 버스정류장이다.", location_idx)
    while True:
        user_input = input("> ")
        if user_input == "q": # 추후 삭제 예정
            break

        elif user_input == "t":
            if check_task():
                task_output(open_task(), "현재 사용자의 임무입니다. (q: 닫기)")
            else:
                main_output("현재 사용자의 임무가 없습니다.", location_idx)

        elif user_input == "v":
            status_output(print_status(), "현재 사용자의 상태입니다. (q: 닫기)")

        elif user_input == "b":
            if check_bag():
                bag_output(
                    open_bag(), "사용할 아이템의 숫자 혹은 이름을 입력하시오. (q: 닫기)"
                )
            else:
                main_output("가방이 비어있습니다.", location_idx)

        elif user_input == "h":
            help_output(
                print_help(),
                "조작법에 해당되는 키를 입력하여 게임을 진행하시오. (q: 닫기)",
            )

        elif user_input == "1":
            main_output("저장할 파일 이름을 입력하시오.", location_idx)
            message = save_game()
            main_output(message, location_idx)

        elif user_input == "2":
            if check_load_empty("saves"):
                main_output("저장된 파일이 없습니다.", location_idx)
            else:
                load_output(
                    "saves", "불러올 파일의 번호를 입력하시오. (0: 폴더 변경 | q: 종료)"
                )

        else:
            message = move_char(user_input)
            main_output(message, location_idx)