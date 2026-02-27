from infra.sql.db_init import PostgresSessionLocal
from infra.sql.repo import AlchemyOrganizationRepo

ACTIVITIES: dict[str, dict[str, list[str] | None]] = {
    "Еда": {
        "Молочные продукты": ["Сыр", "Молоко", "Йогурт", "Сметана"],
        "Мясные продукты": ["Говядина", "Свинина", "Птица", "Колбасы"],
        "Кондитерские изделия": None,
        "Напитки": ["Соки", "Воды", "Лимонады"],
    },
    "Автомобили": {
        "Легковые": ["Седаны", "Хэтчбеки", "Кроссоверы"],
        "Грузовые": ["Фуры", "Самосвалы", "Фургоны"],
        "Запчасти": ["Двигатели", "Кузовные детали", "Электрика"],
    },
    "Спорт": {
        "Тренажёры": ["Беговые дорожки", "Велотренажёры", "Силовые станции"],
        "Командный инвентарь": ["Мячи", "Ворота", "Сетки"],
        "Одежда": ["Футболки", "Кроссовки", "Шорты"],
    },
    "Техника": {
        "Бытовая техника": ["Холодильники", "Стиральные машины", "Пылесосы"],
        "Компьютеры и периферия": ["Ноутбуки", "Мониторы", "Принтеры"],
        "Мобильные устройства": ["Смартфоны", "Планшеты", "Умные часы"],
        "Аксессуары": ["Чехлы", "Зарядные устройства", "Наушники"],
    },
    "Услуги": {
        "Ремонт": ["Автосервис", "Ремонт бытовой техники", "Компьютерный ремонт"],
        "Клининг": ["Уборка квартир", "Мойка окон", "Химчистка"],
        "Образование": ["Курсы иностранных языков", "Программирование", "Репетиторы"],
    },
}


BUILDINGS: list[dict[str, str | float]] = [
    {"address": "ул. Пушкина, д. 10", "latitude": 55.750000, "longitude": 37.620000},
    {"address": "ул. Ленина, д. 15", "latitude": 55.760000, "longitude": 37.630000},
    {"address": "ул. Гагарина, д. 5", "latitude": 55.740000, "longitude": 37.600000},
    {"address": "ул. Садовая, д. 20", "latitude": 55.770000, "longitude": 37.580000},
    {"address": "ул. Мира, д. 8", "latitude": 55.730000, "longitude": 37.650000},
    {"address": "ул. Тверская, д. 12", "latitude": 55.780000, "longitude": 37.620000},
    {"address": "ул. Арбат, д. 3", "latitude": 55.720000, "longitude": 37.600000},
]

ORGANIZATIONS: list[dict[str, str | list[str]]] = [
    {
        "name": "ООО 'Рога и Копыта'",
        "address": "ул. Пушкина, д. 10",
        "numbers": ["7123123123"],
        "activities": ["Молоко", "Мясные продукты"],
    },
    {
        "name": "Пекарня 'Хлебный дом'",
        "address": "ул. Пушкина, д. 10",
        "numbers": ["74953335566"],
        "activities": ["Кондитерские изделия"],
    },
    {
        "name": "Автосалон 'Грузовик'",
        "address": "ул. Пушкина, д. 10",
        "numbers": ["74951238765"],
        "activities": ["Грузовые"],
    },
    {
        "name": "Мясная лавка 'Мясоедов'",
        "address": "ул. Ленина, д. 15",
        "numbers": ["74957654321"],
        "activities": ["Мясные продукты"],
    },
    {
        "name": "Магазин спортивной одежды 'СпортМастер'",
        "address": "ул. Ленина, д. 15",
        "numbers": ["74957779900"],
        "activities": ["Одежда"],
    },
    {
        "name": "Магазин 'Молочный дворик'",
        "address": "ул. Ленина, д. 15",
        "numbers": ["74953339988"],
        "activities": ["Молочные продукты"],
    },
    {
        "name": "Автосалон 'Автомир'",
        "address": "ул. Гагарина, д. 5",
        "numbers": ["74951112233"],
        "activities": ["Легковые"],
    },
    {
        "name": "Автомойка 'Чистюля'",
        "address": "ул. Гагарина, д. 5",
        "numbers": ["74958889911"],
        "activities": ["Автосервис"],
    },
    {
        "name": "Магазин 'Мясо и рыба'",
        "address": "ул. Гагарина, д. 5",
        "numbers": ["74957774455"],
        "activities": ["Мясные продукты"],
    },
    {
        "name": "Магазин автозапчастей 'Запчасть'",
        "address": "ул. Садовая, д. 20",
        "numbers": ["74953334455"],
        "activities": ["Запчасти"],
    },
    {
        "name": "Магазин 'Мобильный мир'",
        "address": "ул. Садовая, д. 20",
        "numbers": ["74951239876"],
        "activities": ["Мобильные устройства", "Аксессуары"],
    },
    {
        "name": "Спортклуб 'Фитнес-арена'",
        "address": "ул. Садовая, д. 20",
        "numbers": ["74958886677"],
        "activities": ["Тренажёры", "Командный инвентарь"],
    },
    {
        "name": "Спортивный клуб 'Фитнес-Холл'",
        "address": "ул. Мира, д. 8",
        "numbers": ["74955556677"],
        "activities": ["Тренажёры", "Одежда"],
    },
    {
        "name": "Сервисный центр 'НоутФикс'",
        "address": "ул. Мира, д. 8",
        "numbers": ["74953456789"],
        "activities": ["Компьютерный ремонт"],
    },
    {
        "name": "Магазин техники 'Эльдорадо'",
        "address": "ул. Мира, д. 8",
        "numbers": ["74959998877"],
        "activities": ["Бытовая техника", "Компьютеры и периферия"],
    },
    {
        "name": "Магазин электроники 'ТехноРай'",
        "address": "ул. Тверская, д. 12",
        "numbers": ["74957778899"],
        "activities": [
            "Бытовая техника",
            "Компьютеры и периферия",
            "Мобильные устройства",
        ],
    },
    {
        "name": "Супермаркет 'Продукты'",
        "address": "ул. Тверская, д. 12",
        "numbers": ["74957894561"],
        "activities": ["Молочные продукты", "Мясные продукты", "Напитки"],
    },
    {
        "name": "Ремонтная мастерская 'Умелые руки'",
        "address": "ул. Тверская, д. 12",
        "numbers": ["74951113344"],
        "activities": ["Ремонт бытовой техники"],
    },
    {
        "name": "Ателье по ремонту телефонов 'iRepair'",
        "address": "ул. Арбат, д. 3",
        "numbers": ["74959990011"],
        "activities": ["Ремонт"],
    },
    {
        "name": "Магазин автозапчастей 'Автодеталь'",
        "address": "ул. Арбат, д. 3",
        "numbers": ["74959871234"],
        "activities": ["Запчасти"],
    },
    {
        "name": "Курсы программирования 'КодКласс'",
        "address": "ул. Арбат, д. 3",
        "numbers": ["74955556688"],
        "activities": ["Программирование"],
    },
]


async def _fill_mock_data(
    org_repo: AlchemyOrganizationRepo,
) -> None:

    activity_name_index: dict[str, int] = {}

    # Добавление типов деятельности
    for first, first_children in ACTIVITIES.items():
        act = await org_repo.add_activity(first)
        activity_name_index[act.name] = act.id

        for second, second_children in first_children.items():
            act = await org_repo.add_activity(second, parent_name=first)
            activity_name_index[act.name] = act.id

            if not second_children:
                continue

            for third in second_children:
                act = await org_repo.add_activity(third, parent_name=second)
                activity_name_index[act.name] = act.id

    building_address_index: dict[str, int] = {}

    for building in BUILDINGS:
        bld = await org_repo.add_building(**building)  # type: ignore
        building_address_index[bld.address] = bld.id

    for organization in ORGANIZATIONS:
        name: str = organization["name"]  # type: ignore
        address: str = organization["address"]  # type: ignore
        building_id = building_address_index[address]
        phone_numbers: list[str] = organization["numbers"]  # type: ignore
        activities: list[str] = organization["activities"]  # type: ignore
        activity_ids = [activity_name_index[a] for a in activities]

        await org_repo.add_org(name, building_id, phone_numbers, activity_ids)


async def fill_db():
    """Наполнить базу данных моковыми организациями."""
    async with PostgresSessionLocal() as session:
        repo = AlchemyOrganizationRepo(session)
        await _fill_mock_data(repo)
