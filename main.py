# ------------------ 모듈 ------------------#
import os


# ------------------ 초기설정 함수 ------------------#

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


# ------------------ 출력 함수 ------------------#

# 초기 출력
def initial_output():
    return


# 기본 출력
def main_output(message: str, loc_idx: list, col: int = 6, row: int = 7):
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


# 상태 출력
def status_output(texts: list, message: str, width: int = 73, height: int = 13):
    while True:
        print("=" * width)
        print(f"[위치]: {location}")
        print(f"[HP]: {char_stat['hp']}")
        print("=" * width)
        for text in texts:
            print(text)
        for _ in range(max(0, height - len(texts))):
            print()
        print("=" * width)
        print(message)
        print("=" * width)
        user_input = input("> ")
        if user_input == "q":
            main_output("상태창을 닫았습니다", location_idx)
            break
        else:
            message = "잘못된 입력입니다."


# 가방 출력
def bag_output(texts: list, message: str, width: int = 73, height: int = 13):
    while True:
        print("=" * width)
        print(f"[위치]: {location}")
        print(f"[HP]: {char_stat['hp']}")
        print("=" * width)
        for text in texts:
            print(text)
        for _ in range(max(0, height - len(texts))):
            print()
        print("=" * width)
        print(message)
        print("=" * width)
        user_input = input("> ")
        if user_input == "q":
            main_output("가방을 닫았습니다.", location_idx)
            break
        else:
            useItem = use_item(user_input)
            if check_bag():
                texts = open_bag()
                message = useItem
            else:
                main_output(useItem, location_idx)
                break


# 불러오기 출력
def load_output(save_dir: str, message: str, width: int = 73, height: int = 13):
    save_dir_ = save_dir
    texts = load_game_list(save_dir)[0]
    dir_list = load_game_list(save_dir)[1]
    change_dir = False
    while True:
        print("=" * width)
        print(f"[위치]: {location}")
        print(f"[HP]: {char_stat['hp']}")
        print("=" * width)
        for text in texts:
            print(text)
        for _ in range(max(0, height - len(texts))):
            print()
        print("=" * width)
        print(message)
        print("=" * width)
            
        if change_dir:
            save_dir = input("> ")
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
            user_input = input("> ")
        
        if user_input == "q":
            main_output("불러오기를 종료합니다.", location_idx)
            break
        elif user_input == "0":
            change_dir = True
            message="변경할 폴더를 입력하세요."
        elif user_input.isdigit() and 1 <= int(user_input) <= len(dir_list):
            file_name = dir_list[int(user_input) - 1]
            message = load_game(save_dir, file_name)
            main_output(message, location_idx)
            break
        else:
            message = "잘못된 입력입니다."


# 상호작용 출력


# ------------------ 이동 함수 ------------------#

# 이동 : 입력이 유효한지 판단 후 이동 출력
def move_char(loc_str: str):
    directions = {
        "w": (0, 1),
        "s": (0, -1),
        "a": (1, -1),
        "d": (1, 1),
    }

    if loc_str not in directions:
        return "잘못된 입력입니다."

    idx, num = directions[loc_str]

    if check_move(location_idx, idx, num):
        char_stat["hp"] -= 1
        global location
        location_idx[idx] += num
        location = schoolMap[location_idx[0]][location_idx[1]]
        return f"{location}(으)로 이동했습니다."
    else:
        return "막힌 방향입니다."


# 이동 유효성 검사 : 불리언 - 이동 가능 여부
def check_move(loc_idx: list, idx: int, num: int) -> bool:
    afterMove = loc_idx.copy()
    afterMove[idx] = afterMove[idx] + num
    validity = True

    try:
        schoolMap[afterMove[0]][afterMove[1]]
        if (afterMove[idx] < 0) or (schoolMap[afterMove[0]][afterMove[1]] == None):
            validity = False
    except IndexError:
        validity = False

    return validity


# ------------------ 상태 함수 ------------------#

# 상태 출력 리스트
def print_status():
    printStat = []
    printStat.append("< 상태창 >")
    printStat.append(f"1. 소지금: {char_stat['money']}원")
    printStat.append(f"2. 체력:   {char_stat['hp']}")
    printStat.append(f"3. 위치: {location}")
    printStat.append(f"4. 동쪽위치: {schoolMap[location_idx[0]][location_idx[1] + 1]}")
    printStat.append(f"5. 서쪽위치: {schoolMap[location_idx[0]][location_idx[1] - 1]}")
    printStat.append(f"6. 남쪽위치: {schoolMap[location_idx[0] - 1][location_idx[1]]}")
    printStat.append(f"7. 북쪽위치: {schoolMap[location_idx[0] + 1][location_idx[1]]}")
    return printStat


# ------------------ 가방 함수 ------------------#

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


# ------------------ 상호작용 함수 ------------------#

# 상호작용 : 지점 도착 시 상호작용 실행
def do_interaction(location: str):
    if location in interaction:
        print(f"\n  ★ {location}에 상점이 있습니다.")
        a = input("  상점에 들어가시겠습니까? [y/n]: ")
        print()
        if a == "y":
            buy_item(location)


# 상호작용 : 아이템 구매하기 - idx 및 이름 기반 처리
def buy_item(location: str):
    while True:
        shop = interaction[location]
        items = list(shop.items())
        print(f"[ {location} 상점 ] - 소지금 {char_stat['money']}원\n")
        for i, (name, stock) in enumerate(items, 1):
            price = item_dict[name][0]
            print(f"  {i}. {name}  {price}원  (재고: {stock})")
        buy_input = input("구매할 아이템 번호 입력 (q: 닫기): ")

        if buy_input == "q":
            break

        name = None
        if buy_input.isdigit():
            idx = int(buy_input) - 1
            if 0 <= idx < len(items):
                name = items[idx][0]
            else:
                print("  없는 번호입니다.")
                continue
        elif buy_input in shop:
            name = buy_input
        else:
            print("  없는 아이템입니다.")
            continue

        price = item_dict[name][0]
        if shop[name] <= 0:
            print("  재고가 없습니다.")
        elif char_stat["money"] >= price:
            char_stat["money"] -= price
            shop[name] -= 1
            if name in char_stat["bag"]:
                char_stat["bag"][name] += 1
            else:
                char_stat["bag"][name] = 1
            print(f"\n  → {name} 구매 완료 (잔액: {char_stat['money']}원)")
        else:
            print(
                f"\n  돈이 부족합니다. (필요: {price}원, 보유: {char_stat['money']}원)"
            )


# ------------------ 난이도 설정 함수 ------------------#

# 난이도 설정 : idx 및 이름 기반 처리 - 시작 및 게임 도중 호출 ### 추후 반영 예정
def set_difficulty():
    difficulty = ["쉬움", "보통", "어려움"]
    prepGame = True
    while prepGame:
        prepGame = False
        diff = input("난이도를 설정하시오 - [1. 쉬움, 2. 보통, 3. 어려움]: ")
        if diff == "1" or diff == "쉬움":
            settings["difficulty"] = difficulty[0]
        elif diff == "2" or diff == "보통":
            settings["difficulty"] = difficulty[1]
        elif diff == "3" or diff == "어려움":
            settings["difficulty"] = difficulty[2]
        else:
            print("\n  잘못된 입력입니다\n")
            prepGame = True
    print(f"  난이도가 {settings['difficulty']}으로 설정되었습니다.")


# ------------------ 게임 저장/불러오기 함수 ------------------#

# 게임 저장하기 : 폴더 생성 후 각 요소 추가하기 ++ 임무, 모든 입력
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
    file_list = [f for f in os.listdir(save_dir) if not f.startswith('.') and f.endswith('.txt')]
    load_list = []
    load_list.append("< 저장된 파일 목록 >")
    for i, file in enumerate(file_list):
        load_list.append(f"{i + 1}. {file}")
    return load_list, file_list


# 저장 폴더 확인 : 폴더가 없거나 파일이 없으면 True 반환
def check_load_empty(save_dir: str):
    if not os.path.isdir(save_dir):
        return True
    file_list = [f for f in os.listdir(save_dir) if not f.startswith('.') and f.endswith('.txt')]
    if len(file_list) == 0:
        return True
    return False


# 게임 불러오기 : 파일 선택 후 각 요소 불러오기
def load_game(save_dir, file_name):
    global char_stat, location, location_idx, env_stat
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


# ------------------ 변수 목록 ------------------#

# 주인공 상태 -> 딕셔너리
char_stat = {"hp": 10, "stamina": "배고픔", "money": 50000, "bag": {}}

# 아이템 -> 딕셔너리 - [가격, 회복량]
item_dict = {"두쫀쿠": [2500, 25], "카페라떼": [5000, 25]}

# 상호작용 -> 딕셔너리 - [가격, 재고]
interaction = {"학생회관": {"두쫀쿠": 50, "카페라떼": 100}}

# 위치 -> 리스트 - [x, y]
location = "연대앞 버스정류장"
location_idx = [0, 0]

# 학교 위치 -> 연대앞 버스정류장 ~ 이윤재관
school_locations = [
    "연대앞 버스정류장", "정문", "스타벅스", "세브란스병원 버스정류장", None, None, 
    "공학원","백양로1", "공터1", "암병원", "의과대학", None, 
    "공학관","백양로2", "백주년기념관", "안과병원", "제중관", None, 
    "체육관","백양로3", "공터2", "광혜원", "어린이병원", "세브란스병원", 
    "중앙도서관","독수리상", "학생회관", "루스채플", "재활병원", "치과대학", 
    "백양관","백양로5", "대강당", "음악관", "알렌관", "ABMRC", 
    None, None, None, None, "새천년관", "이윤재관",
]

# 함수 생성 -> 학교 지도 및 좌표 - n개의 열을 가지는 지도 생성
schoolMap = create_map(6, school_locations)

# 설정 -> 딕셔너리 - 난이도
settings = {"difficulty": "보통"}

# ------------------ 메인 함수 ------------------#
if __name__ == "__main__":
    main_output(
        "[w/a/s/d]이동 [f]상호작용 [v]상태창 [t]임무 [b]가방 [1/2]저장/불러오기 [q]종료",
        location_idx,
    )
    while True:
        user_input = input("> ")
        if user_input == "q":
            break

        elif user_input == "v":
            status_output(print_status(), "현재 사용자의 상태입니다(q: 상태창 닫기)")

        elif user_input == "b":
            if check_bag():
                bag_output(
                    open_bag(),
                    "사용할 아이템의 숫자 혹은 이름을 입력하시오(q: 가방 닫기)",
                )
            else:
                main_output("가방이 비어있습니다.", location_idx)

        elif user_input == "1":
            main_output("저장할 파일 이름을 입력하세요: ", location_idx)
            message = save_game()
            main_output(message, location_idx)

        elif user_input == "2":
            if check_load_empty("saves"):
                main_output("저장된 파일이 없습니다.", location_idx)
            else:
                load_output("saves", "불러올 파일의 번호를 입력하세요(0: 폴더 변경 | q: 종료)")

        else:
            message = move_char(user_input)
            main_output(message, location_idx)
