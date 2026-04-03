# ------------------ 함수 목록 ------------------#

# 지도 생성 -> 리스트 - 지도, 지도 좌표
def create_map(col: int, location: list) -> list:
    schoolMap = []
    rMap = []
    for idx, loc in enumerate(location):
        rMap.append(loc)
        if (idx + 1) % col == 0:
            schoolMap.append(rMap)
            rMap = []
    return schoolMap


# 이동 -> 입력이 유효한지 판단 후 이동 출력
def move_char(loc_str: str):
    print("\n" + SEP)
    char_stat["hp"] -= 1
    directions = {
        "w": (0, 1),
        "s": (0, -1),
        "a": (1, -1),
        "d": (1, 1),
    }

    if loc_str not in directions:
        print("  잘못된 입력입니다.")
        return 

    idx, num = directions[loc_str]

    if check_move(location_idx, idx, num):
        location_idx[idx] += num
        location = schoolMap[location_idx[0]][location_idx[1]]
        print(f"  현재 위치: {location}")
        doInteraction(location)
    else:
        print("  막힌 방향입니다.")

    print(SEP)
    


# 이동 유효성 검사 -> 불리언 - 이동 가능 여부
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


# 상태 출력
def print_status():
    print("\n" + SEP)
    print("[ 상태 ]")
    print(f"  체력:   {char_stat['hp']}")
    print(f"  소지금: {char_stat['money']}원")
    print(SEP)


# 가방 열기
def open_bag():
    while True:
        print("\n" + SEP)
        print("[ 가방 ]")
        if not char_stat["bag"]:
            print("  가방이 비어있습니다.")
            print(SEP)
            break
        for i, (name, count) in enumerate(char_stat["bag"].items(), 1):
            hp_recover = item_dict[name][1]
            print(f"  {i}. {name}  x{count}  (HP +{hp_recover})")
        print(SEP)
        user_input = input("사용할 아이템 번호 입력 (q: 닫기): ")
        if user_input == "q":
            break
        use_item(user_input)


# 아이템 사용
def use_item(user_input: str):
    items = list(char_stat["bag"].items())

    if user_input.isdigit():
        idx = int(user_input) - 1
        if 0 <= idx < len(items):
            name = items[idx][0]
        else:
            print("  없는 번호입니다.")
            return
    elif user_input in char_stat["bag"]:
        name = user_input
    else:
        print("  가방에 없는 아이템입니다.")
        return

    recover = item_dict[name][1]
    char_stat["hp"] += recover
    char_stat["bag"][name] -= 1
    print(f"\n  → {name} 사용 (HP +{recover}, 현재 HP: {char_stat['hp']})")
    clean_inventory()


# 가방 정리 : 0개인 아이템 제거
def clean_inventory():
    char_stat["bag"] = {k: v for k, v in char_stat["bag"].items() if v != 0}


# 상호작용 - 지점 도착 시 상호작용 실행
def doInteraction(location: str):
    if location in interaction:
        print(SEP)
        print(f"\n  ★ {location}에 상점이 있습니다.")
        a = input("  상점에 들어가시겠습니까? [y/n]: ")
        if a == "y":
            buy_item(location)


# 상호작용 - 아이템 구매하기
def buy_item(location: str):
    while True:
        shop = interaction[location]
        items = list(shop.items())
        print("\n" + SEP)
        print(f"[ {location} 상점 ] - 사용자 소지금 {char_stat['money']}원\n")
        for i, (name, stock) in enumerate(items, 1):
            price = item_dict[name][0]
            print(f"  {i}. {name}  {price}원  (재고: {stock})")
        print(SEP)
        buy_input = input("구매할 아이템 번호 입력 (q: 닫기): ")
        print()

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
            print(f"  → {name} 구매 완료 (잔액: {char_stat['money']}원)")
        else:
            print(f"  돈이 부족합니다. (필요: {price}원, 보유: {char_stat['money']}원)")


# ------------------ 변수 목록 ------------------#

# 출력 구분선
SEP = "-" * 40

# 주인공 상태 -> 딕셔너리
char_stat = {
    "hp": 10, 
    "stamina": "배고픔", 
    "money": 50000, 
    "bag": {"두쫀쿠": 1}
}

# 환경 상태 -> 딕셔너리 - 시간
env_stat = {
    "time": 1100
}

# 아이템 -> 딕셔너리 - [가격, 회복량]
item_dict = {
    "두쫀쿠": [2500, 25], 
    "카페라떼": [5000, 25]
}

# 상호작용 -> 딕셔너리 - [가격, 재고]
interaction = {
    "학생회관": {"두쫀쿠": 50, "카페라떼": 100}
}

# 위치 -> 리스트 - [x, y]
location = "연대앞 버스정류장"
location_idx = [0, 0]

# 학교 위치 -> 연대앞 버스정류장 ~ 이윤재관
school_locations = [
    "연대앞버스정류장", "정문", "스타벅스", "세브란스병원버스정류장", None, None,
    "공학원", "백양로1", "공터1", "암병원", "의과대학", None,
    "공학관", "백양로2", "백주년기념관", "안과병원", "제중관", None,
    "체육관", "백양로3", "공터2", "광혜원", "어린이병원", "세브란스병원",
    "중앙도서관", "독수리상", "학생회관", "루스채플", "재활병원", "치과대학",
    "백양관", "백양로5", "대강당", "음악관", "알렌관", "ABMRC",
    None, None, None, None, "새천년관", "이윤재관",
]

# 함수 생성 -> 학교 지도 및 좌표 - n개의 열을 가지는 지도 생성
schoolMap = create_map(6, school_locations)

# 설정 -> 딕셔너리 - 난이도
settings = {"difficulty": ["쉬움", "보통", "어려움"]}


# ------------------ 메인 함수 ------------------#
if __name__ == "__main__":
    print("\n" + "=" * 40)
    print(f"  출발! 당신은 지금 {location}에 있습니다.")
    print("=" * 40)
    print("  조작: 이동(w/a/s/d) | 가방(b) | 상태(v) | 종료(q)")

    while True:
        user_input = input("\n입력: ")

        if user_input == "q":
            print("\n" + SEP)
            print("게임을 종료합니다")
            break

        elif user_input == "v":
            print_status()

        elif user_input == "b":
            open_bag()

        else:
            move_char(user_input)
