import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def main():
    sheet_id = os.environ.get('SPREADSHEET_ID')
    service_account_info = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_KEY'))
    
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    client = gspread.authorize(creds)
    
    # 指定開啟名稱為 "image" 的分頁
    try:
        sheet = client.open_by_key(sheet_id).worksheet("image")
    except gspread.exceptions.WorksheetNotFound:
        print("錯誤：在 Google Sheet 中找不到名為 'image' 的分頁。")
        return

    # 讀取目前表格中已有的圖片網址（假設網址在 B 欄 / index 1）
    existing_records = sheet.get_all_values()
    existing_urls = [row[1] for row in existing_records if len(row) > 1]
    
    repo_owner = os.environ.get('GITHUB_REPOSITORY_OWNER')
    repo_name = os.environ.get('GITHUB_REPOSITORY').split('/')[1]
    
    base_dir = 'images'
    
    # 對應你截圖中的大寫資料夾名稱：PTCG 與 PTCGP
    categories = {
        'PTCG': 'PTCG',
        'PTCGP': 'PTCGP'
    }
    
    # 支援的圖片格式副檔名
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    rows_to_add = []
    
    # 掃描 PTCG 及 PTCGP 資料夾
    for folder, category_name in categories.items():
        folder_path = os.path.join(base_dir, folder)
        
        if os.path.exists(folder_path):
            for filename in sorted(os.listdir(folder_path)):
                # 確保只處理圖片檔案，跳過 test.txt 或 .gitkeep
                if filename.lower().endswith(valid_extensions):
                    # 構建 GitHub CDN Raw 圖片網址
                    raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{base_dir}/{folder}/{filename}"
                    
                    if raw_url not in existing_urls:
                        # 寫入格式：A欄 (檔名) | B欄 (圖片網址) | C欄 (類別: PTCG / PTCGP)
                        rows_to_add.append([filename, raw_url, category_name])
    
    # 新增新資料至 Google Sheet
    if rows_to_add:
        sheet.append_rows(rows_to_add)
        print(f"成功新增 {len(rows_to_add)} 筆圖片資料至 'image' 分頁！")
    else:
        print("沒有新圖片需要更新。")

if __name__ == '__main__':
    main()
