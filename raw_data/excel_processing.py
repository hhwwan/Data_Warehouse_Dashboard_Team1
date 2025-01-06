import openpyxl
import os

"""
연도별 매출액 상위 20개 영화만 남기고 다 삭제
"""

# 엑셀 파일이 있는 디렉토리 경로
directory_path = "C:/Users/hwan/Desktop/project_2/cumulative sales"  # 수정 필요
output_directory = "C:/Users/hwan/Desktop/project_2/cumulative sales/processing"  # 저장할 디렉토리 경로

# 디렉토리 내 모든 엑셀 파일 처리
for filename in os.listdir(directory_path):
    if filename.endswith(".xlsx"):  # 엑셀 파일만 처리
        file_path = os.path.join(directory_path, filename)
        
        # 엑셀 파일 열기
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active

        # 행 삭제: 23행부터 마지막 행까지 삭제
        max_row = sheet.max_row
        if max_row > 22:
            sheet.delete_rows(23, max_row - 22)

        # 변경된 내용을 새로운 디렉토리에 저장
        updated_path = os.path.join(output_directory, "processing_" + filename)
        wb.save(updated_path)
        wb.close()
        print(f"'{filename}' 처리 완료, 저장 경로: {updated_path}")

print("모든 파일 처리 완료!")
