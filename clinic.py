import os
os.environ["FLET_SERVER_PORT"] = "8501"
os.environ["FLET_SERVER_IP"] = "0.0.0.0"
import sqlite3
import pandas as pd
import os

# 1. إعداد قاعدة البيانات وتحديث الجداول
def init_db():
    conn = sqlite3.connect("clinic_data.db")
    cursor = conn.cursor()
    # التأكد من وجود كافة الأعمدة المطلوبة
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT, 
                       age TEXT, 
                       status TEXT)''')
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "نظام العيادة المتطور"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 900
    page.window_height = 800
    # تفعيل التمرير في الصفحة الرئيسية لمواجهة أي تداخل
    page.scroll = ft.ScrollMode.ADAPTIVE
    
    init_db()

    # متغير لعرض إجمالي المرضى
    total_patients_card = ft.Text("0", size=30, weight="bold", color="blue")
    
    def update_stats():
        conn = sqlite3.connect("clinic_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM patients")
        total = cursor.fetchone()[0]
        total_patients_card.value = str(total)
        conn.close()
        page.update()

    def export_to_excel(e):
        try:
            conn = sqlite3.connect("clinic_data.db")
            df = pd.read_sql_query("SELECT * FROM patients", conn)
            df.columns = ['ID', 'الاسم', 'العمر', 'التشخيص']
            df.to_excel("سجل_العيادة.xlsx", index=False)
            conn.close()
            page.snack_bar = ft.SnackBar(ft.Text("تم تصدير ملف الإكسل بنجاح!"), bgcolor="green")
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"خطأ في التصدير: {ex}"), bgcolor="red")
            page.snack_bar.open = True
        page.update()

    def delete_patient(patient_id):
        conn = sqlite3.connect("clinic_data.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        conn.close()
        load_data()
        update_stats()

    def load_data():
        patients_table.rows.clear()
        conn = sqlite3.connect("clinic_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients")
        for row in cursor.fetchall():
            p_id = row[0]
            patients_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(p_id))),
                    ft.DataCell(ft.Text(row[1], weight="bold")),
                    ft.DataCell(ft.Text(row[2])),
                    ft.DataCell(ft.Text(row[3])),
                    ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_SWEEP, icon_color="red", on_click=lambda e, id=p_id: delete_patient(id))),
                ])
            )
        conn.close()
        page.update()

    def save_patient(e):
        if name_input.value:
            conn = sqlite3.connect("clinic_data.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO patients (name, age, status) VALUES (?, ?, ?)", 
                           (name_input.value, age_input.value, status_input.value))
            conn.commit()
            conn.close()
            name_input.value = ""; age_input.value = ""; status_input.value = ""
            load_data()
            update_stats()

    # واجهة الإدخال
    name_input = ft.TextField(label="اسم المريض", expand=True, prefix_icon=ft.Icons.PERSON)
    age_input = ft.TextField(label="العمر", width=100, prefix_icon=ft.Icons.NUMBERS)
    status_input = ft.TextField(label="التشخيص الطبي", expand=True, prefix_icon=ft.Icons.MEDICAL_SERVICES)
    
    # تعريف الجدول
    patients_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("الاسم")),
            ft.DataColumn(ft.Text("العمر")),
            ft.DataColumn(ft.Text("التشخيص")),
            ft.DataColumn(ft.Text("إجراء")),
        ],
        rows=[]
    )

    # منطقة الجدول القابلة للتمرير (Scrolling)
    table_scroll_area = ft.Column(
        [patients_table],
        scroll=ft.ScrollMode.ALWAYS,
        height=400, # ارتفاع منطقة العرض
        expand=True
    )

    # تجميع الواجهة
    page.add(
        ft.AppBar(title=ft.Text("عيادة الدكتور الاحترافية"), bgcolor="blue_800", color="white"),
        ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Column([ft.Text("إحصائية المرضى"), total_patients_card], horizontal_alignment="center"),
                        bgcolor="blue_50", padding=20, border_radius=15, expand=True
                    ),
                    ft.ElevatedButton("تصدير إكسل", icon=ft.Icons.FILE_DOWNLOAD, on_click=export_to_excel, height=70)
                ]),
                ft.Row([name_input, age_input]),
                ft.Row([status_input, ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=save_patient)]),
                ft.Divider(),
                ft.Text("سجل المراجعات", size=20, weight="bold"),
                ft.Container(content=table_scroll_area, border=ft.border.all(1, "grey300"), border_radius=10, padding=10)
            ], spacing=20)
        )
    )

    load_data()
    update_stats()

ft.app(target=main, view=ft.AppView.WEB_BROWSER)