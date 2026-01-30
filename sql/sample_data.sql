-- ============================================================================
-- SAMPLE DATA FOR MULTI-AGENT DEBATE SYSTEM
-- ============================================================================
-- This file contains sample financial data for testing the system.
-- Run this after setup_all.sql to populate tables with test data.
-- ============================================================================

USE DATABASE FINANCIAL_RESEARCH;
USE SCHEMA EQUITY_RESEARCH;

-- ============================================================================
-- 1. INVESTMENT METRICS (10 stocks)
-- ============================================================================

INSERT INTO INVESTMENT_METRICS (
    TICKER, COMPANY_NAME, METRIC_DATE,
    PE_RATIO, FORWARD_PE, PEG_RATIO, PRICE_TO_BOOK, PRICE_TO_SALES, EV_TO_EBITDA,
    ROE_PCT, ROA_PCT, GROSS_MARGIN_PCT, OPERATING_MARGIN_PCT, NET_MARGIN_PCT,
    DEBT_TO_EQUITY, CURRENT_RATIO, QUICK_RATIO,
    DIVIDEND_YIELD_PCT, PAYOUT_RATIO_PCT,
    REVENUE_GROWTH_YOY_PCT, EARNINGS_GROWTH_YOY_PCT,
    MARKET_CAP_BILLIONS, ENTERPRISE_VALUE_BILLIONS, SHARES_OUTSTANDING_MILLIONS
)
VALUES
    ('NVDA', 'NVIDIA Corporation', CURRENT_DATE(),
     65.2, 45.8, 1.8, 42.5, 28.3, 52.1, 85.2, 45.3, 75.8, 62.4, 55.2,
     0.45, 4.2, 3.8, 0.03, 1.2, 122.5, 168.3, 2850.5, 2820.3, 2450.0),
    ('AAPL', 'Apple Inc.', CURRENT_DATE(),
     28.5, 26.2, 2.4, 45.8, 7.2, 21.5, 147.2, 28.5, 45.2, 30.8, 25.3,
     1.82, 1.05, 0.92, 0.52, 15.2, 2.8, 8.5, 2950.2, 2980.5, 15400.0),
    ('MSFT', 'Microsoft Corporation', CURRENT_DATE(),
     35.2, 31.5, 2.1, 12.5, 12.8, 24.8, 38.5, 18.2, 70.2, 45.5, 35.8,
     0.35, 1.85, 1.72, 0.72, 25.5, 15.2, 22.8, 3150.8, 3120.5, 7450.0),
    ('GOOGL', 'Alphabet Inc.', CURRENT_DATE(),
     24.8, 21.2, 1.5, 6.2, 5.8, 15.2, 28.5, 15.8, 57.5, 28.2, 24.5,
     0.08, 2.15, 2.02, 0.0, 0.0, 12.5, 28.5, 1980.5, 1850.2, 12850.0),
    ('AMZN', 'Amazon.com Inc.', CURRENT_DATE(),
     42.5, 35.8, 1.8, 8.5, 2.8, 18.5, 22.5, 8.2, 47.5, 10.2, 7.8,
     0.58, 1.08, 0.85, 0.0, 0.0, 18.5, 85.2, 1920.5, 1950.8, 10450.0),
    ('TSLA', 'Tesla Inc.', CURRENT_DATE(),
     55.8, 48.2, 2.5, 12.8, 8.5, 35.2, 22.8, 8.5, 18.2, 9.5, 12.5,
     0.12, 1.72, 1.45, 0.0, 0.0, 8.5, -15.2, 785.2, 750.5, 3180.0),
    ('META', 'Meta Platforms Inc.', CURRENT_DATE(),
     28.2, 24.5, 1.2, 8.2, 7.5, 14.8, 32.5, 18.5, 81.5, 35.2, 28.5,
     0.15, 2.85, 2.72, 0.42, 12.5, 22.5, 45.8, 1350.5, 1280.2, 2580.0),
    ('AMD', 'Advanced Micro Devices Inc.', CURRENT_DATE(),
     125.5, 42.8, 1.5, 4.2, 10.5, 45.2, 3.5, 1.8, 52.5, 5.2, 4.5,
     0.05, 2.52, 2.15, 0.0, 0.0, 45.2, 125.5, 285.5, 275.2, 1620.0),
    ('NFLX', 'Netflix Inc.', CURRENT_DATE(),
     45.2, 35.5, 2.2, 15.8, 8.2, 28.5, 32.5, 12.5, 45.8, 22.5, 18.2,
     0.72, 1.15, 1.02, 0.0, 0.0, 15.8, 52.5, 285.2, 295.5, 435.0),
    ('CRM', 'Salesforce Inc.', CURRENT_DATE(),
     52.5, 28.5, 1.8, 4.5, 7.8, 22.5, 8.5, 4.2, 75.2, 18.5, 12.5,
     0.18, 1.05, 0.95, 0.0, 0.0, 11.2, 85.2, 285.5, 275.8, 975.0);

-- ============================================================================
-- 2. EARNINGS HISTORY (16 quarters across companies)
-- ============================================================================

INSERT INTO EARNINGS_HISTORY (
    TICKER, COMPANY_NAME, FISCAL_QUARTER, FISCAL_YEAR, REPORT_DATE,
    EPS_ACTUAL, EPS_ESTIMATE, EPS_SURPRISE, EPS_SURPRISE_PCT,
    REVENUE_ACTUAL_MILLIONS, REVENUE_ESTIMATE_MILLIONS, REVENUE_SURPRISE_MILLIONS, REVENUE_SURPRISE_PCT,
    BEAT_MISS, GUIDANCE_EPS_LOW, GUIDANCE_EPS_HIGH, REPORT_TIME
)
VALUES
    -- NVIDIA
    ('NVDA', 'NVIDIA Corporation', 'Q4', 2024, '2024-02-21',
     5.16, 4.59, 0.57, 12.4, 22103, 20378, 1725, 8.5, 'BEAT', 5.45, 5.65, 'AFTER_MARKET'),
    ('NVDA', 'NVIDIA Corporation', 'Q3', 2024, '2023-11-21',
     4.02, 3.36, 0.66, 19.6, 18120, 16178, 1942, 12.0, 'BEAT', 4.85, 5.05, 'AFTER_MARKET'),
    ('NVDA', 'NVIDIA Corporation', 'Q2', 2024, '2023-08-23',
     2.70, 2.07, 0.63, 30.4, 13507, 11045, 2462, 22.3, 'BEAT', 3.85, 4.05, 'AFTER_MARKET'),
    ('NVDA', 'NVIDIA Corporation', 'Q1', 2024, '2023-05-24',
     1.09, 0.92, 0.17, 18.5, 7192, 6521, 671, 10.3, 'BEAT', 2.45, 2.65, 'AFTER_MARKET'),
    -- Apple
    ('AAPL', 'Apple Inc.', 'Q1', 2024, '2024-02-01',
     2.18, 2.10, 0.08, 3.8, 119575, 117925, 1650, 1.4, 'BEAT', 2.05, 2.15, 'AFTER_MARKET'),
    ('AAPL', 'Apple Inc.', 'Q4', 2023, '2023-11-02',
     1.46, 1.39, 0.07, 5.0, 89498, 89285, 213, 0.2, 'BEAT', 1.95, 2.05, 'AFTER_MARKET'),
    ('AAPL', 'Apple Inc.', 'Q3', 2023, '2023-08-03',
     1.26, 1.19, 0.07, 5.9, 81797, 81692, 105, 0.1, 'BEAT', 1.35, 1.45, 'AFTER_MARKET'),
    ('AAPL', 'Apple Inc.', 'Q2', 2023, '2023-05-04',
     1.52, 1.43, 0.09, 6.3, 94836, 92858, 1978, 2.1, 'BEAT', 1.20, 1.30, 'AFTER_MARKET'),
    -- Microsoft
    ('MSFT', 'Microsoft Corporation', 'Q2', 2024, '2024-01-30',
     2.93, 2.78, 0.15, 5.4, 62020, 61120, 900, 1.5, 'BEAT', 2.85, 2.95, 'AFTER_MARKET'),
    ('MSFT', 'Microsoft Corporation', 'Q1', 2024, '2023-10-24',
     2.99, 2.65, 0.34, 12.8, 56517, 54535, 1982, 3.6, 'BEAT', 2.70, 2.80, 'AFTER_MARKET'),
    -- Tesla
    ('TSLA', 'Tesla Inc.', 'Q4', 2023, '2024-01-24',
     0.71, 0.74, -0.03, -4.1, 25167, 25755, -588, -2.3, 'MISS', 0.65, 0.75, 'AFTER_MARKET'),
    ('TSLA', 'Tesla Inc.', 'Q3', 2023, '2023-10-18',
     0.66, 0.73, -0.07, -9.6, 23350, 24065, -715, -3.0, 'MISS', 0.70, 0.80, 'AFTER_MARKET'),
    -- Meta
    ('META', 'Meta Platforms Inc.', 'Q4', 2023, '2024-02-01',
     5.33, 4.96, 0.37, 7.5, 40111, 39125, 986, 2.5, 'BEAT', 4.85, 5.15, 'AFTER_MARKET'),
    ('META', 'Meta Platforms Inc.', 'Q3', 2023, '2023-10-25',
     4.39, 3.63, 0.76, 20.9, 34146, 33545, 601, 1.8, 'BEAT', 4.15, 4.45, 'AFTER_MARKET'),
    -- AMD
    ('AMD', 'Advanced Micro Devices Inc.', 'Q4', 2023, '2024-01-30',
     0.77, 0.77, 0.00, 0.0, 6168, 6125, 43, 0.7, 'MEET', 0.75, 0.85, 'AFTER_MARKET'),
    ('AMD', 'Advanced Micro Devices Inc.', 'Q3', 2023, '2023-10-31',
     0.70, 0.68, 0.02, 2.9, 5800, 5695, 105, 1.8, 'BEAT', 0.72, 0.82, 'AFTER_MARKET');

-- ============================================================================
-- 3. TECHNICAL INDICATORS
-- ============================================================================

INSERT INTO TECHNICAL_INDICATORS (
    TICKER, INDICATOR_DATE, CLOSE_PRICE, VOLUME,
    SMA_20, SMA_50, SMA_200, RSI_14, RSI_SIGNAL,
    MACD, MACD_SIGNAL, MACD_HISTOGRAM
)
VALUES
    ('NVDA', CURRENT_DATE(), 875.50, 45000000, 845.20, 785.50, 525.80, 68.5, 'NEUTRAL', 12.5, 10.2, 2.3),
    ('AAPL', CURRENT_DATE(), 185.25, 52000000, 182.50, 178.20, 172.50, 55.2, 'NEUTRAL', 2.8, 2.5, 0.3),
    ('MSFT', CURRENT_DATE(), 415.80, 22000000, 408.50, 385.20, 342.80, 62.5, 'NEUTRAL', 8.5, 7.2, 1.3),
    ('GOOGL', CURRENT_DATE(), 155.20, 28000000, 152.80, 145.50, 128.20, 58.8, 'NEUTRAL', 3.2, 2.8, 0.4),
    ('AMZN', CURRENT_DATE(), 182.50, 48000000, 178.20, 165.80, 142.50, 65.2, 'NEUTRAL', 5.5, 4.8, 0.7),
    ('TSLA', CURRENT_DATE(), 185.50, 98000000, 195.20, 225.50, 245.80, 35.2, 'OVERSOLD', -8.5, -5.2, -3.3),
    ('META', CURRENT_DATE(), 485.20, 15000000, 472.50, 425.80, 345.20, 72.5, 'OVERBOUGHT', 15.2, 12.5, 2.7),
    ('AMD', CURRENT_DATE(), 175.80, 55000000, 168.50, 155.20, 125.80, 58.5, 'NEUTRAL', 5.8, 5.2, 0.6),
    ('NFLX', CURRENT_DATE(), 605.50, 5500000, 585.20, 545.80, 425.50, 68.2, 'NEUTRAL', 18.5, 15.2, 3.3),
    ('CRM', CURRENT_DATE(), 295.20, 6500000, 285.50, 268.20, 225.80, 55.8, 'NEUTRAL', 5.2, 4.8, 0.4);

-- ============================================================================
-- 4. MARKET SENTIMENT
-- ============================================================================

INSERT INTO MARKET_SENTIMENT (
    TICKER, COMPANY_NAME, SENTIMENT_DATE,
    NEWS_SENTIMENT_SCORE, NEWS_ARTICLE_COUNT,
    SOCIAL_MEDIA_SENTIMENT_SCORE, SOCIAL_MENTION_COUNT,
    OVERALL_SENTIMENT, BULLISH_PCT, BEARISH_PCT, NEUTRAL_PCT,
    ANALYST_RATING_AVG, PRICE_TARGET_AVG
)
VALUES
    ('NVDA', 'NVIDIA Corporation', CURRENT_DATE(), 0.85, 245, 0.78, 15420, 'VERY_BULLISH', 78.5, 12.5, 9.0, 4.8, 950.00),
    ('AAPL', 'Apple Inc.', CURRENT_DATE(), 0.45, 185, 0.52, 28500, 'BULLISH', 58.2, 22.5, 19.3, 4.2, 205.00),
    ('MSFT', 'Microsoft Corporation', CURRENT_DATE(), 0.72, 165, 0.68, 12850, 'BULLISH', 68.5, 15.2, 16.3, 4.5, 475.00),
    ('GOOGL', 'Alphabet Inc.', CURRENT_DATE(), 0.55, 142, 0.48, 9850, 'BULLISH', 55.8, 25.2, 19.0, 4.1, 175.00),
    ('AMZN', 'Amazon.com Inc.', CURRENT_DATE(), 0.62, 178, 0.58, 18520, 'BULLISH', 62.5, 20.5, 17.0, 4.3, 210.00),
    ('TSLA', 'Tesla Inc.', CURRENT_DATE(), -0.25, 385, -0.15, 85200, 'BEARISH', 35.2, 48.5, 16.3, 3.2, 175.00),
    ('META', 'Meta Platforms Inc.', CURRENT_DATE(), 0.68, 125, 0.72, 7520, 'BULLISH', 65.8, 18.2, 16.0, 4.4, 550.00),
    ('AMD', 'Advanced Micro Devices Inc.', CURRENT_DATE(), 0.58, 95, 0.62, 8520, 'BULLISH', 62.5, 22.5, 15.0, 4.0, 195.00),
    ('NFLX', 'Netflix Inc.', CURRENT_DATE(), 0.52, 85, 0.48, 5250, 'BULLISH', 55.2, 28.5, 16.3, 3.8, 650.00),
    ('CRM', 'Salesforce Inc.', CURRENT_DATE(), 0.45, 72, 0.42, 3850, 'NEUTRAL', 48.5, 28.2, 23.3, 3.9, 325.00);

-- ============================================================================
-- 5. ANALYST REPORTS (For Cortex Search)
-- ============================================================================

INSERT INTO ANALYST_REPORTS (
    REPORT_ID, TICKER, COMPANY_NAME, FIRM, ANALYST_NAME,
    REPORT_DATE, REPORT_TITLE, REPORT_TYPE, RATING, PRICE_TARGET,
    REPORT_SUMMARY, REPORT_CONTENT
)
VALUES
    ('RPT-NVDA-001', 'NVDA', 'NVIDIA Corporation', 'Goldman Sachs', 'Toshiya Hari',
     CURRENT_DATE() - 5, 'NVIDIA: AI Leadership Continues to Drive Unprecedented Growth', 'UPDATE', 'BUY', 1000.00,
     'NVIDIA continues to dominate the AI chip market with its H100 and upcoming B100 GPUs. Data center revenue growth exceeds expectations.',
     'NVIDIA Corporation (NVDA) continues to demonstrate exceptional execution in the rapidly growing AI infrastructure market. The company''s H100 GPU has become the de facto standard for AI training workloads, and early indications suggest the upcoming B100 will further extend NVIDIA''s technological lead. Key investment thesis points: 1) Data center revenue grew 409% YoY, driven by unprecedented demand for AI training and inference. 2) Gross margins expanded to 76% as the company benefits from pricing power and scale. 3) The software moat through CUDA continues to strengthen with over 4 million developers in the ecosystem. 4) Supply constraints are gradually easing as TSMC increases CoWoS capacity. We raise our price target to $1,000 based on 45x CY25 EPS of $22.22. Risks include potential demand normalization, increased competition from AMD and custom silicon, and geopolitical tensions affecting China sales.'),
    
    ('RPT-NVDA-002', 'NVDA', 'NVIDIA Corporation', 'Morgan Stanley', 'Joseph Moore',
     CURRENT_DATE() - 12, 'NVIDIA: Blackwell Architecture Sets New Performance Bar', 'UPDATE', 'OVERWEIGHT', 950.00,
     'Blackwell GPU architecture promises 4x performance improvement for AI inference workloads. Maintaining Overweight rating.',
     'NVIDIA''s announcement of the Blackwell GPU architecture represents a significant leap forward in AI computing capabilities. The B100 and B200 GPUs deliver up to 4x improvement in AI inference performance compared to the H100, while the GB200 NVL72 superchip configuration enables unprecedented scale for large language model training. Investment highlights: 1) Blackwell''s transformer engine with FP4 precision opens new efficiency frontiers for inference. 2) NVLink Switch enables 72 GPU configurations with 130TB/s bandwidth. 3) Enterprise software stack (NeMo, NIM) accelerates customer adoption. 4) Automotive and robotics segments provide long-term growth optionality. We maintain our Overweight rating and $950 price target.'),
    
    ('RPT-AAPL-001', 'AAPL', 'Apple Inc.', 'JP Morgan', 'Samik Chatterjee',
     CURRENT_DATE() - 8, 'Apple: Services Growth Offsets iPhone Softness', 'UPDATE', 'OVERWEIGHT', 215.00,
     'Services segment delivers 11% growth and record margins. iPhone 16 cycle expected to drive upgrade momentum.',
     'Apple Inc. delivered a solid quarter with Services revenue reaching an all-time high of $23.1B, growing 11% YoY with gross margins expanding to 74.5%. While iPhone revenue declined 6% YoY due to market saturation in key regions, we believe the iPhone 16 cycle with Apple Intelligence features will drive a meaningful upgrade cycle. Key points: 1) Services now represents 25% of total revenue with significantly higher margins. 2) Installed base of active devices exceeded 2.2 billion, up 8% YoY. 3) Apple Intelligence features exclusive to iPhone 15 Pro and newer create compelling upgrade incentive. 4) Vision Pro opens new platform opportunity. We maintain Overweight with a $215 price target based on 30x CY25 EPS.'),
    
    ('RPT-TSLA-001', 'TSLA', 'Tesla Inc.', 'Bernstein', 'Toni Sacconaghi',
     CURRENT_DATE() - 3, 'Tesla: Near-Term Challenges but Long-Term Vision Intact', 'UPDATE', 'HOLD', 180.00,
     'Margin pressure continues as price cuts impact profitability. FSD progress and Robotaxi remain key catalysts.',
     'Tesla''s Q4 results reflect ongoing challenges in the EV market with automotive gross margins declining to 17.6% from 25.9% a year ago due to aggressive pricing actions. However, we believe the long-term autonomous driving opportunity remains compelling. Analysis: 1) Vehicle deliveries of 484K missed expectations. 2) Energy storage grew 75% YoY to $1.4B. 3) FSD V12 shows promising improvements with end-to-end neural network approach. 4) Cybertruck ramp continues with production expected to reach 250K/year by end of 2024. We maintain Hold rating with $180 price target.');

-- ============================================================================
-- 6. EARNINGS TRANSCRIPTS (For Cortex Search)
-- ============================================================================

INSERT INTO EARNINGS_TRANSCRIPTS (
    TRANSCRIPT_ID, TICKER, COMPANY_NAME, CALL_DATE, FISCAL_QUARTER, FISCAL_YEAR,
    CALL_TYPE, CEO_NAME, CFO_NAME, TRANSCRIPT_TITLE, TRANSCRIPT_SUMMARY, TRANSCRIPT_CONTENT,
    OVERALL_TONE
)
VALUES
    ('TRX-NVDA-Q4-24', 'NVDA', 'NVIDIA Corporation', '2024-02-21 17:00:00', 'Q4', 2024,
     'EARNINGS', 'Jensen Huang', 'Colette Kress',
     'NVIDIA Q4 FY2024 Earnings Call Transcript',
     'CEO Jensen Huang highlighted accelerating demand for AI infrastructure and introduced new Blackwell architecture.',
     'Jensen Huang - CEO: Thank you for joining us today. NVIDIA delivered another exceptional quarter with record revenue of $22.1 billion, up 265% from a year ago. The era of generative AI is here, and NVIDIA is at the center of this transformation. Our data center revenue of $18.4 billion grew 409% year-over-year as enterprises and cloud providers race to deploy AI infrastructure. We are seeing demand across every industry vertical - from healthcare to financial services to manufacturing. Our H100 GPU has become the engine of the AI revolution, and we are now ramping production of the next-generation Blackwell architecture. Blackwell delivers a 4x improvement in AI inference performance and enables training of trillion-parameter models. Looking ahead, the $1 trillion installed base of data center infrastructure is being upgraded to accelerated computing. Colette Kress - CFO: Revenue for Q4 was $22.1 billion, up 22% sequentially and 265% from a year ago. Data center revenue was a record $18.4 billion. Gross margin was 76.7%. We returned $2.8 billion to shareholders through dividends and buybacks.',
     'POSITIVE'),
    
    ('TRX-AAPL-Q1-24', 'AAPL', 'Apple Inc.', '2024-02-01 17:00:00', 'Q1', 2024,
     'EARNINGS', 'Tim Cook', 'Luca Maestri',
     'Apple Q1 FY2024 Earnings Call Transcript',
     'CEO Tim Cook announced Apple Intelligence features coming to iPhone, iPad, and Mac. Services achieved all-time revenue record.',
     'Tim Cook - CEO: Good afternoon everyone. I am pleased to report that Apple had a strong holiday quarter with revenue of $119.6 billion. We achieved all-time revenue records in Services, Mac, and iPad. iPhone revenue was $69.7 billion. Our installed base of active devices reached an all-time high of over 2.2 billion, which continues to fuel our Services growth. Services reached an all-time record of $23.1 billion in revenue, growing 11% year-over-year. Looking ahead, we are incredibly excited about Apple Intelligence, our personal intelligence system that combines large language models with personal context. Apple Intelligence will be available on iPhone 15 Pro, iPad Pro, and Mac with M-series chips. We believe Apple Intelligence will create a compelling reason for customers to upgrade their devices. Luca Maestri - CFO: Total revenue was $119.6 billion. Gross margin was 45.9%, up 90 basis points year-over-year. We generated operating cash flow of $39.9 billion and returned over $27 billion to shareholders.',
     'POSITIVE');

-- ============================================================================
-- Verification Queries
-- ============================================================================

SELECT 'Investment Metrics' as table_name, COUNT(*) as row_count FROM INVESTMENT_METRICS
UNION ALL SELECT 'Earnings History', COUNT(*) FROM EARNINGS_HISTORY
UNION ALL SELECT 'Technical Indicators', COUNT(*) FROM TECHNICAL_INDICATORS
UNION ALL SELECT 'Market Sentiment', COUNT(*) FROM MARKET_SENTIMENT
UNION ALL SELECT 'Analyst Reports', COUNT(*) FROM ANALYST_REPORTS
UNION ALL SELECT 'Earnings Transcripts', COUNT(*) FROM EARNINGS_TRANSCRIPTS;
