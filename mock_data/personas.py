"""Mock Vietnamese micro-SME personas using Taiwan Credit Card Dataset native variables."""

PERSONAS = {
    'borrower_001': {
        'name': 'Nguyễn Thị Hoa',
        'business_name': 'Tạp hóa Hoa Phát',
        'business_type': 'household_retail',
        'scenario': 'Chủ tạp hóa — có lịch sử ngân hàng tốt',
        'loan_purpose': 'Nhập thêm hàng hóa cho mùa Tết',
        'loan_amount_requested': 50_000_000,
        'expected_decision': 'APPROVE',
        'profile': {
            'gender': 'female',
            'age_group': '35-45',
            'employment_type': 'household_business',
            'region': 'suburban',
            'province': 'Hà Nội'
        },
        'bank_data': {
            'LIMIT_BAL': 50_000_000.0,
            'SEX': 2,
            'EDUCATION': 2,
            'MARRIAGE': 1,
            'AGE': 40,
            'PAY_0': 0,
            'PAY_2': 0,
            'PAY_3': 0,
            'BILL_AMT1': 10_000_000.0,
            'PAY_AMT1': 12_000_000.0
        },
        'utility_data': {'provider': 'EVN + VNPT', 'months_history': 48, 'on_time_rate': 0.98},
        'mobile_data': {'platform': 'MoMo', 'consistency_score': 0.91, 'monthly_volume': 35_000_000}
    },
    'borrower_002': {
        'name': 'Trần Văn Minh',
        'business_name': 'Xe bánh mì Minh',
        'business_type': 'street_vendor',
        'scenario': 'Người bán hàng rong — thin-file, chỉ có mobile money',
        'loan_purpose': 'Mua xe đẩy mới và nguyên liệu',
        'loan_amount_requested': 15_000_000,
        'expected_decision': 'APPROVE',
        'profile': {
            'gender': 'male',
            'age_group': '25-35',
            'employment_type': 'street_vendor',
            'region': 'urban',
            'province': 'TP.HCM'
        },
        'bank_data': None,
        'utility_data': {'provider': 'EVN', 'months_history': 36, 'on_time_rate': 0.95},
        'mobile_data': {'platform': 'ZaloPay', 'consistency_score': 0.87, 'monthly_volume': 18_000_000}
    },
    'borrower_003': {
        'name': 'Lê Thị Lan',
        'business_name': 'Quán cơm bình dân Lan',
        'business_type': 'food_stall',
        'scenario': 'Chủ quán cơm — borderline, thu nhập không ổn định',
        'loan_purpose': 'Sửa chữa bếp và mua thiết bị',
        'loan_amount_requested': 30_000_000,
        'expected_decision': 'ESCALATE',
        'profile': {
            'gender': 'female',
            'age_group': '35-45',
            'employment_type': 'food_stall_owner',
            'region': 'suburban',
            'province': 'Đà Nẵng'
        },
        'bank_data': {
            'LIMIT_BAL': 30_000_000.0,
            'SEX': 2,
            'EDUCATION': 3,
            'MARRIAGE': 1,
            'AGE': 38,
            'PAY_0': 1,
            'PAY_2': 1,
            'PAY_3': 0,
            'BILL_AMT1': 18_000_000.0,
            'PAY_AMT1': 2_000_000.0
        },
        'utility_data': {'provider': 'EVN', 'months_history': 24, 'on_time_rate': 0.82},
        'mobile_data': {'platform': 'ViettelPay', 'consistency_score': 0.63, 'monthly_volume': 12_000_000}
    },
    'borrower_004': {
        'name': 'Phạm Văn Đức',
        'business_name': 'Dịch vụ sửa xe Đức',
        'business_type': 'repair_service',
        'scenario': 'Thợ sửa xe — rủi ro cao, nhiều khoản nợ',
        'loan_purpose': 'Mua thiết bị sửa chữa',
        'loan_amount_requested': 40_000_000,
        'expected_decision': 'DENY',
        'profile': {
            'gender': 'male',
            'age_group': '25-35',
            'employment_type': 'self_employed',
            'region': 'rural',
            'province': 'Bình Dương'
        },
        'bank_data': {
            'LIMIT_BAL': 40_000_000.0,
            'SEX': 1,
            'EDUCATION': 3,
            'MARRIAGE': 2,
            'AGE': 28,
            'PAY_0': 3,
            'PAY_2': 2,
            'PAY_3': 2,
            'BILL_AMT1': 35_000_000.0,
            'PAY_AMT1': 500_000.0
        },
        'utility_data': {'provider': 'EVN', 'months_history': 12, 'on_time_rate': 0.62},
        'mobile_data': {'platform': 'MoMo', 'consistency_score': 0.38, 'monthly_volume': 6_000_000}
    },
    'borrower_005': {
        'name': 'Võ Thị Thu',
        'business_name': 'Shop thời trang online Thu',
        'business_type': 'online_retail',
        'scenario': 'Bán hàng online — thin-file nhưng doanh thu MoMo cao',
        'loan_purpose': 'Nhập hàng cho mùa sale 11/11',
        'loan_amount_requested': 25_000_000,
        'expected_decision': 'APPROVE',
        'profile': {
            'gender': 'female',
            'age_group': '18-25',
            'employment_type': 'online_seller',
            'region': 'urban',
            'province': 'TP.HCM'
        },
        'bank_data': None,
        'utility_data': {'provider': 'VNPT', 'months_history': 18, 'on_time_rate': 0.93},
        'mobile_data': {'platform': 'MoMo', 'consistency_score': 0.88, 'monthly_volume': 45_000_000}
    },
    'borrower_006': {
        'name': 'Nguyễn Văn Bình',
        'business_name': 'Nông hộ Bình — trồng rau sạch',
        'business_type': 'agriculture',
        'scenario': 'Nông dân — thu nhập theo mùa vụ, không có ngân hàng',
        'loan_purpose': 'Mua hạt giống và phân bón vụ mới',
        'loan_amount_requested': 20_000_000,
        'expected_decision': 'ESCALATE',
        'profile': {
            'gender': 'male',
            'age_group': '45-55',
            'employment_type': 'farmer',
            'region': 'rural',
            'province': 'Long An'
        },
        'bank_data': None,
        'utility_data': {'provider': 'EVN', 'months_history': 60, 'on_time_rate': 0.91},
        'mobile_data': {'platform': 'ViettelPay', 'consistency_score': 0.72, 'monthly_volume': 8_000_000}
    }
}
