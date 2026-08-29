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
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    rows_to_add = []
    
    # 使用 os.walk 自動遞迴掃描所有層級的子資料夾
    if os.path.exists(base_dir):
        for root, dirs, files in os.walk(base_dir):
            for filename in sorted(files):
                if filename.lower().endswith(valid_extensions):
                    # 取得相對路徑（例如：PTCG/CHT 或 PTCGP）
                    rel_dir = os.path.relpath(root, base_dir)
                    
                    # 統一將路徑分隔符換成網址專用的正斜線 /
                    url_rel_path = rel_dir.replace('\\', '/')
                    
                    # 構建 Raw 圖片網址
                    raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{base_dir}/{url_rel_path}/{filename}"
                    
                    if raw_url not in existing_urls:
                        filename_without_ext = os.path.splitext(filename)[0]
                        
                        # 組合 Column C 識別碼：將層級路徑改為底線連接
                        # 範例 1：images/PTCG/CHT/m1L_091.jpg -> PTCG_CHT_m1L_091
                        # 範例 2：images/PTCGP/A1_1.webp -> PTCGP_A1_1
                        path_prefix = rel_dir.replace('\\', '_').replace('/', '_')
                        column_c_value = f"{path_prefix}_{filename_without_ext}"
                        
                        # 寫入格式：A欄 (檔名) | B欄 (圖片網址) | C欄 (類別與識別碼)
                        rows_to_add.append([filename, raw_url, column_c_value])
    
    # 新增新資料至 Google Sheet
    if rows_to_add:
        sheet.append_rows(rows_to_add)
        print(f"成功新增 {len(rows_to_add)} 筆圖片資料至 'image' 分頁！")
    else:
        print("沒有新圖片需要更新。")

if __name__ == '__main__':
    main()
