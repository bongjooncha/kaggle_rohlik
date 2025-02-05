import pandas as pd
import numpy as np

## abd_base에서 사용했던 푸리에 변환
def fourier(df):
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.month_name()
    df['day_of_week'] = df['date'].dt.day_name()
    df['week'] = df['date'].dt.isocalendar().week
    df['year_sin'] = np.sin(2 * np.pi * df['year'])
    df['year_cos'] = np.cos(2 * np.pi * df['year'])
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12) 
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['day_sin'] = np.sin(2 * np.pi * df['day'] / 31)  
    df['day_cos'] = np.cos(2 * np.pi * df['day'] / 31)
    df['group'] = (df['year'] - 2020) * 48 + df['month'] * 4 + df['day'] // 7
    
    df.drop('date', axis=1, inplace=True)
    
    cols = ['warehouse', 'month_name', 'day_of_week','holiday_name','L1_category_name_en',
             'L2_category_name_en','L3_category_name_en','L4_category_name_en']
    df['holiday_name'] = df['holiday_name'].fillna('None')
    for c in cols:
        df[c] = df[c].astype('category')


## lamav6weighted에서 사용했던 휴일 계산
def process_calendar(df):
    """
    Обрабатывает календарный датафрейм, добавляя новые колонки:
    - days_to_holiday
    - days_to_shops_closed
    - day_after_closing
    - long_weekend
    - weekday
    """
    # Убеждаемся, что даты отсортированы
    df = df.sort_values('date').reset_index(drop=True)
    
    # 1. days_to_holiday
    df['next_holiday_date'] = df.loc[df['holiday'] == 1, 'date'].shift(-1)
    df['next_holiday_date'] = df['next_holiday_date'].bfill()
    df['days_to_holiday'] = (df['next_holiday_date'] - df['date']).dt.days
    df.drop(columns=['next_holiday_date'], inplace=True)
    
    # 2. days_to_shops_closed
    df['next_shops_closed_date'] = df.loc[df['shops_closed'] == 1, 'date'].shift(-1)
    df['next_shops_closed_date'] = df['next_shops_closed_date'].bfill()
    df['days_to_shops_closed'] = (df['next_shops_closed_date'] - df['date']).dt.days
    df.drop(columns=['next_shops_closed_date'], inplace=True)
    
    # 3. day_after_closing
    df['day_after_closing'] = (
        (df['shops_closed'] == 0) & (df['shops_closed'].shift(1) == 1)
    ).astype(int)
    
    # 4. long_weekend
    df['long_weekend'] = (
        (df['shops_closed'] == 1) & (df['shops_closed'].shift(1) == 1)
    ).astype(int)
    
    # 5. weekday
    df['weekday'] = df['date'].dt.weekday  # 0 (понедельник) - 6 (воскресенье)
    return df

def day_off(calendar):
    Frankfurt_1 = calendar.query('date >= "2020-08-01 00:00:00" and warehouse =="Frankfurt_1"')
    Prague_2 = calendar.query('date >= "2020-08-01 00:00:00" and warehouse =="Prague_2"')
    Brno_1 = calendar.query('date >= "2020-08-01 00:00:00" and warehouse =="Brno_1"')
    Munich_1 = calendar.query('date >= "2020-08-01 00:00:00" and warehouse =="Munich_1"')
    Prague_3 = calendar.query('date >= "2020-08-01 00:00:00" and warehouse =="Prague_3"')
    Prague_1 = calendar.query('date >= "2020-08-01 00:00:00" and warehouse =="Prague_1"')
    Budapest_1 = calendar.query('date >= "2020-08-01 00:00:00" and warehouse =="Budapest_1"')

    dfs = ['Frankfurt_1', 'Prague_2', 'Brno_1', 'Munich_1', 'Prague_3', 'Prague_1', 'Budapest_1']
    processed_dfs = [process_calendar(globals()[df]) for df in dfs]

    # Конкатенируем все датафреймы в один
    calendar_extended = pd.concat(processed_dfs).sort_values('date').reset_index(drop=True)
    return calendar_extended

