import pandas as pd

df = pd.DataFrame({'code': ['3KPRG2501716', '3KPRG2501717', '3KPRG2501718', '3KPRG2501719', '3KPRG2501720',
                            '3KPRG2501721', '3KPRG2501722', '3KPRG2501723', '3KPRG2501724', '3KPRG2501725',
                            '3KPRG2501726', '3KPRG2501727', '3KPRG2501728', '3KPRG2501729', '3KPRG2501730',
                            '3KPRG2501731', '3KPRG2501732', '3KPRG2501733', '3KPRG2501734', '3KPRG2501735',
                            '3KPRG2501736', '3KPRG2501737', '3KPRG2501738', '3KPRG2501739', '3KPRG2501740']})


df.to_csv("codes.csv", index=False)
print("CSV file 'codes.csv' created with sample data.")