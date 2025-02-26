import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

file_path = 'emigrate_ict.csv'
df = pd.read_csv(file_path)

df['location_country'] = df['location_country'].fillna('').astype(str).str.strip().str.lower()
total_profiles = len(df)
top_country = df['location_country'].mode()[0] if not df['location_country'].isna().all() else 'نامشخص'
total_migrants = df['location_country'].nunique()


if 'history[0].type' in df.columns:
    edu_counts = df['history[0].type'].fillna('نامشخص').value_counts().reset_index()
    edu_counts.columns = ['education_type', 'count']
    fig_edu_bar = px.bar(edu_counts, x='education_type', y='count',
                         title='محبوب‌ترین نوع تحصیلات',
                         labels={'education_type': 'نوع تحصیلات', 'count': 'تعداد'})
else:
    fig_edu_bar = px.bar(title='محبوب‌ترین نوع تحصیلات (داده موجود نیست)')

if 'history[0].end_date' in df.columns:
    df['graduation_year'] = pd.to_datetime(df['history[0].end_date'], errors='coerce').dt.year
    edu_timeline = df.groupby(['graduation_year', 'history[0].type']).size().reset_index(name='count')
    fig_edu_line = px.line(edu_timeline.dropna(), x='graduation_year', y='count',
                           color='history[0].type',
                           title='تغییرات تحصیلی در طول زمان',
                           labels={'graduation_year': 'سال فارغ‌التحصیلی', 'count': 'تعداد', 'history[0].type': 'نوع تحصیلات'})
else:
    fig_edu_line = px.line(title='تغییرات تحصیلی (داده موجود نیست)')


if 'history[1].type' in df.columns:
    job_counts = df['history[1].type'].fillna('نامشخص').value_counts().reset_index()
    job_counts.columns = ['job_type', 'count']
    fig_job_bar = px.bar(job_counts, x='job_type', y='count',
                         title='محبوب‌ترین مشاغل',
                         labels={'job_type': 'نوع شغل', 'count': 'تعداد'})
else:
    fig_job_bar = px.bar(title='محبوب‌ترین مشاغل (داده موجود نیست)')

if 'history[1].start_date' in df.columns:
    df['job_start_year'] = pd.to_datetime(df['history[1].start_date'], errors='coerce').dt.year
    job_timeline = df.groupby(['job_start_year', 'history[1].type']).size().reset_index(name='count')
    fig_job_line = px.line(job_timeline.dropna(), x='job_start_year', y='count',
                           color='history[1].type',
                           title='تغییرات مشاغل در طول زمان',
                           labels={'job_start_year': 'سال شروع شغل', 'count': 'تعداد', 'history[1].type': 'نوع شغل'})
else:
    fig_job_line = px.line(title='تغییرات مشاغل (داده موجود نیست)')

if 'history[0].type' in df.columns and 'history[1].type' in df.columns:
    pivot = pd.crosstab(df['history[0].type'].fillna('نامشخص'),
                        df['history[1].type'].fillna('نامشخص'))
    fig_heatmap = px.imshow(pivot, text_auto=True, aspect="auto",
                            title='ارتباط بین نوع تحصیلات و نوع شغل')
else:
    fig_heatmap = px.imshow([[0]], text_auto=True, title='ارتباط بین تحصیلات و شغل (داده موجود نیست)')


dest_counts = df['location_country'].value_counts().reset_index()
dest_counts.columns = ['country', 'count']
fig_mig_bar = px.bar(dest_counts, x='country', y='count',
                     title='کشورهای مقصد اصلی مهاجرت متخصصان ICT',
                     labels={'country': 'کشور', 'count': 'تعداد متخصصان'})

if 'exit_type' in df.columns:
    mig_type_counts = df['exit_type'].fillna('نامشخص').value_counts().reset_index()
    mig_type_counts.columns = ['exit_type', 'count']
    fig_mig_pie = px.pie(mig_type_counts, values='count', names='exit_type',
                         title='نسبت انواع خروج (مهاجرت)')
else:
    fig_mig_pie = px.pie(title='نسبت انواع خروج (داده موجود نیست)')

if 'job_start_year' in df.columns and 'exit_type' in df.columns:
    fig_scatter = px.strip(df, x='job_start_year', y='exit_type',
                           title='ارتباط بین سال شروع شغل و نوع خروج',
                           labels={'job_start_year': 'سال شروع شغل', 'exit_type': 'نوع خروج'})
else:
    fig_scatter = px.scatter(title='ارتباط بین سال شروع شغل و نوع خروج (داده موجود نیست)')


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("داشبورد تحلیل متخصصان ICT و مهاجرت", style={'textAlign': 'center', 'marginBottom': '20px'}),
    html.H3("طراحی و تولید : مهران علم بیگی", style={'textAlign': 'center', 'marginBottom': '20px'}),
    dcc.Tabs([
        dcc.Tab(label='تحلیل تحصیلی', children=[
            html.Div([
                html.H2("محبوب‌ترین نوع تحصیلات"),
                dcc.Graph(figure=fig_edu_bar),
                html.H2("تغییرات تحصیلی در طول زمان"),
                dcc.Graph(figure=fig_edu_line)
            ], style={'padding': '20px'})
        ]),
        dcc.Tab(label='تحلیل شغلی', children=[
            html.Div([
                html.H2("محبوب‌ترین مشاغل"),
                dcc.Graph(figure=fig_job_bar),
                html.H2("تغییرات مشاغل در طول زمان"),
                dcc.Graph(figure=fig_job_line),
                html.H2("ارتباط بین تحصیلات و مشاغل"),
                dcc.Graph(figure=fig_heatmap)
            ], style={'padding': '20px'})
        ]),
        dcc.Tab(label='تحلیل مهاجرت', children=[
            html.Div([
                html.H2("کشورهای مقصد مهاجرت"),
                dcc.Graph(figure=fig_mig_bar),
                html.H2("نسبت انواع خروج (مهاجرت)"),
                dcc.Graph(figure=fig_mig_pie),
                html.H2("ارتباط بین سال شروع شغل و نوع خروج"),
                dcc.Graph(figure=fig_scatter)
            ], style={'padding': '20px'})
        ]),
        dcc.Tab(label='داشبورد کلی', children=[
            html.Div([
                html.H2("شاخص‌های کلیدی", style={'textAlign': 'center'}),
                html.Div([
                    html.Div([
                        html.H3("👤 تعداد کل متخصصان"),
                        html.P(f"{total_profiles:,}")
                    ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px', 'border': '1px solid gray'}),
                    
                    html.Div([
                        html.H3("🌍 محبوب‌ترین مقصد مهاجرت"),
                        html.P(f"{top_country}")
                    ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px', 'border': '1px solid gray'}),

                    html.Div([
                        html.H3("📊 تعداد کشورهای مقصد"),
                        html.P(f"{total_migrants}")
                    ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px', 'border': '1px solid gray'}),
                ], style={'textAlign': 'center'}),
                
                html.H2("خلاصه تحلیل‌ها"),
                html.P("در این بخش خلاصه‌ای از محبوب‌ترین مشاغل، رشته‌های تحصیلی و کشورهای مقصد مهاجرت نمایش داده می‌شود."),
                
                html.Div([
                    html.Div([
                        html.H3("🎓 محبوب‌ترین رشته‌های تحصیلی"),
                        dcc.Graph(figure=fig_edu_bar)
                    ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
                    
                    html.Div([
                        html.H3("💼 محبوب‌ترین مشاغل"),
                        dcc.Graph(figure=fig_job_bar)
                    ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
                ], style={'textAlign': 'center'}),
                
                html.Div([
                    html.H3("🌎 کشورهای مقصد مهاجرت"),
                    dcc.Graph(figure=fig_mig_bar)
                ], style={'width': '80%', 'margin': 'auto', 'padding': '10px'})
            ], style={'padding': '20px'})
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
