#!/usr/bin/env python3
"""
CDC NHSN Weekly Hospital Respiratory Surveillance Data Analysis & Visualization Script.
Generates publication-grade charts from NHSN surveillance data.
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    os.makedirs('visualizations', exist_ok=True)
    sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')
    chart_dpi = 150

    # Load data
    data_path = 'Weekly_Hospital_Respiratory_Admission_Levels_and_Rates_by_J.csv'
    if not os.path.exists(data_path):
        data_path = '/workspace/knowledge/Weekly_Hospital_Respiratory_Admission_Levels_and_Rates_by_J.csv'

    df = pd.read_csv(data_path)

    # Clean numeric columns
    numeric_cols = ['totalConfC19NewAdm', 'totalConfFluNewAdm', 'totalConfRSVNewAdm',
                    'totalConfC19NewAdmPer100k', 'totalConfFluNewAdmPer100k', 'totalConfRSVNewAdmPer100k']

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').astype(float)

    df['weekEndingDate'] = pd.to_datetime(df['weekEndingDate'])

    # 1. National Respiratory Trends Line Chart
    usa_df = df[df['jurisdiction']=='USA'].sort_values('weekEndingDate')

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.lineplot(data=usa_df, x='weekEndingDate', y='totalConfC19NewAdm', ax=ax, label='COVID-19', linewidth=2.8, color='#d95f02')
    sns.lineplot(data=usa_df, x='weekEndingDate', y='totalConfFluNewAdm', ax=ax, label='Influenza', linewidth=2.5, color='#7570b3')
    sns.lineplot(data=usa_df, x='weekEndingDate', y='totalConfRSVNewAdm', ax=ax, label='RSV', linewidth=2.5, color='#1b9e77')

    ax.set_title('COVID-19 Hospital Admissions Surged 355% From June Lows (Apr-Sep 2026)', fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Week Ending Date', fontweight='bold')
    ax.set_ylabel('Weekly New Hospital Admissions', fontweight='bold')
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b %d'))
    ax.set_ylim(0, 4400)

    latest_c19 = usa_df['totalConfC19NewAdm'].iloc[-1]
    latest_date = usa_df['weekEndingDate'].iloc[-1]
    min_c19 = usa_df['totalConfC19NewAdm'].min()
    min_date = usa_df.loc[usa_df['totalConfC19NewAdm'] == min_c19, 'weekEndingDate'].values[0]

    ax.annotate(f'Peak: {latest_c19:,.0f} admissions\n(Sep 05)', xy=(latest_date, latest_c19),
                xytext=(latest_date - pd.Timedelta(days=35), latest_c19 + 100),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                fontweight='bold', fontsize=9)

    ax.annotate(f'Low: {min_c19:,.0f}\n(Jun 20)', xy=(min_date, min_c19),
                xytext=(min_date - pd.Timedelta(days=15), min_c19 + 600),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                fontweight='bold', fontsize=9)

    ax.text(0.01, -0.12, 'Source: CDC National Healthcare Safety Network (NHSN) Respiratory Surveillance Data (2026)',
            transform=ax.transAxes, fontsize=8, color='gray')

    sns.despine()
    plt.tight_layout(pad=1.5)
    fig.savefig('/workspace/scratch/national_respiratory_trends.png', dpi=chart_dpi, bbox_inches='tight')
    plt.close()

    # 2. Top Jurisdictions Admission Rates
    latest_dt = df['weekEndingDate'].max()
    latest_df = df[(df['weekEndingDate'] == latest_dt) & (df['jurisdiction'] != 'USA')].copy()
    latest_df['total_rate'] = latest_df['totalConfC19NewAdmPer100k'].fillna(0) + latest_df['totalConfFluNewAdmPer100k'].fillna(0) + latest_df['totalConfRSVNewAdmPer100k'].fillna(0)
    top10 = latest_df.sort_values('total_rate', ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top10, x='total_rate', y='jurisdiction', ax=ax, palette='Blues_r')

    for c in ax.containers:
        ax.bar_label(c, fmt='%.2f', fontweight='bold', padding=4)

    ax.set_title('Alaska & Florida Lead US Jurisdictions in Respiratory Hospitalizations (Sep 2026)', fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Total Hospital Admissions per 100,000 Population', fontweight='bold')
    ax.set_ylabel('Jurisdiction', fontweight='bold')

    ax.text(0.01, -0.12, 'Source: CDC NHSN Data (Week ending Sep 05, 2026). Combined COVID-19, Flu, and RSV admission rate per 100k.',
            transform=ax.transAxes, fontsize=8, color='gray')

    sns.despine()
    plt.tight_layout(pad=1.5)
    fig.savefig('/workspace/scratch/top_jurisdictions_admission_rates.png', dpi=chart_dpi, bbox_inches='tight')
    plt.close()

    # 3. Pathogen Disease Burden Breakdown
    fig, ax = plt.subplots(figsize=(10, 6))
    top10_plot = top10.set_index('jurisdiction')[['totalConfC19NewAdmPer100k', 'totalConfFluNewAdmPer100k', 'totalConfRSVNewAdmPer100k']]
    top10_plot.columns = ['COVID-19', 'Influenza', 'RSV']

    top10_plot.plot(kind='barh', stacked=True, ax=ax, color=['#d95f02', '#7570b3', '#1b9e77'], width=0.7)

    ax.set_title('COVID-19 Accounts for Over 70% of Hospitalization Rate Across Top States', fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Admissions per 100,000 Population', fontweight='bold')
    ax.set_ylabel('Jurisdiction', fontweight='bold')
    ax.legend(title='Pathogen', frameon=True)
    ax.invert_yaxis()

    ax.text(0.01, -0.12, 'Source: CDC NHSN Surveillance Data (Week ending Sep 05, 2026).',
            transform=ax.transAxes, fontsize=8, color='gray')

    sns.despine()
    plt.tight_layout(pad=1.5)
    fig.savefig('/workspace/scratch/pathogen_disease_burden_breakdown.png', dpi=chart_dpi, bbox_inches='tight')
    plt.close()

    print('Analysis complete. Visualizations generated successfully.')

if __name__ == '__main__':
    main()
