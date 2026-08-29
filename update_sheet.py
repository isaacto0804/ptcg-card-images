import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 設定 Google Sheets API 權限範圍
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def main():
    # 讀取 Secrets
    sheet_id = os.environ.get('SPREADSHEET_ID')
    service_account_info = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_KEY'))
    
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    client = gspread.authorize(creds)
    
    # 開啟試算表（預設第一個工作表）
    sheet = client.open_by_key(sheet_id).worksheet("image")
    
    # 讀取目前表格中已有的資料，避免重複寫入
    existing_records = sheet.get_all_values()
    existing_urls = [row[1] for row in existing_records if len(row) > 1]
    
    # GitHub 帳號與倉庫資訊
    repo_owner = os.environ.get('GITHUB_REPOSITORY_OWNER')
    repo_name = os.environ.get('GITHUB_REPOSITORY').split('/')[1]
    
    # 掃描 images/ 目錄下的圖片
    image_dir = 'images'
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    
    rows_to_add = []
    
    if os.path.exists(image_dir):
        for filename in sorted(os.listdir(image_dir)):
            if filename.lower().endswith(valid_extensions):
                # 構建 GitHub CDN Raw 圖片網址
                raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{image_dir}/{filename}"
                
                if raw_url not in existing_urls:
                    # 欄位：檔名, 圖片網址
                    rows_to_add.append([filename, raw_url])
    
    # 新增新資料到 Google Sheet
    if rows_to_add:
        sheet.append_rows(rows_to_add)
        print(f"成功新增 {len(rows_to_add)} 張圖片資料至 Google Sheet！")
    else:
        print("沒有新圖片需要更新。")

if __name__ == '__main__':
    main()
