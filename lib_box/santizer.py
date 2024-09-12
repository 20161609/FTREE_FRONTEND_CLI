from datetime import datetime


# Formats an integer amount into currency format with the Korean Won symbol.
def format_cost(amount):
    return f"{amount:,.0f}"


# Formats Date Value into format on SQL
# Convert the string to a datetime object. The string should be in the format 'YYYY-MM-DD'.
def format_date(date_str: str):
    if len(date_str) == 6:
        s = f'20{date_str}'
        return s[:4:] + '-' + s[4:6:] + '-' + s[6::]

    current_year = datetime.now().year

    # Define date formats to try
    date_formats = [
        '%Y%m%d',  # '20230513'
        '%Y/%m/%d',  # '2023/05/13'
        '%Y-%m-%d',  # '2023-05-13'
        '%y/%m/%d',  # '23/05/13'
        '%y-%m-%d',  # '23-05-13'
        '%y/%m/%d',  # '23/5/13'
        '%y-%m-%d',  # '23-5-13'
        '%m/%d',  # '5/13'
        '%m-%d'  # '5-13'
    ]

    for fmt in date_formats:
        try:
            # Try parsing the date string with the current format
            date = datetime.strptime(date_str, fmt)
            # If the format doesn't include the year, add the current year
            if '%y' not in fmt and '%Y' not in fmt:
                date = date.replace(year=current_year)
            return str(date.strftime('%Y-%m-%d'))
        except ValueError:
            continue

    # If none of the formats match, return None
    return None


def format_month(date_str: str):
    current_year = datetime.now().year

    # Define date formats to try
    date_formats = [
        '%Y%m',  # 1. '202305'
        '%y%m',  # 2. '2305'
        '%Y/%m',  # 3. '2023/05'
        '%Y-%m',  # 4. '2023-05'
        '%y/%m',  # 5. '23/05'
        '%y-%m',  # 6. '23-05'
        '%y/%m',  # 7. '23/5'
        '%y-%m',  # 8. '23-5'
        '%m',  # 9. '5'
    ]

    for fmt in date_formats:
        try:
            # Try parsing the date string with the current format
            date = datetime.strptime(date_str, fmt)
            # If the format doesn't include the year, add the current year
            if '%y' not in fmt and '%Y' not in fmt:
                date = date.replace(year=current_year)
            return str(date.strftime('%Y-%m'))
        except ValueError:
            continue

    # If none of the formats match, return None
    return None


# Monday, Tuesday, Wednesday, ...
def day_of_week(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    days = ["Mon", "Tue", "Wed", "Thurs", "Fri", "Sat", "Sun"]
    return days[date.weekday()]


# Check Validity and Compose File Name
invalid_characters = {"\\", "/", ":", "*", "?", "\"", "<", ">", "|", "!", "_", " "}
def is_valid_txt(txt):
    return not any(char in txt for char in invalid_characters)


# Input Validation
def make_image_file_name(_date, _branch, _cashflow, _description):
    # Validate - Date
    temp_date = _date
    _date = format_date(_date)
    if _date is None:
        valid_date_formats = [
            '19960513', '960513', '1996/05/13', '1996-05-13',
            '96/05/13', '96-05-13', '96/5/13', '96-5-13'
        ]

        return {
            'status': False,
            'tag': f"Invalid date format. Please enter the date in one of the following formats: {', '.join(valid_date_formats)}. You entered: '{temp_date}'."
        }

    # Validate - Branch
    _branch = _branch.replace('/', '-')
    if not _branch:
        return {
            'status': False,
            'tag': 'Branch name is required.'
        }

    # Validate - cash flow
    try:
        _cashflow = f"{'+' if int(_cashflow) > 0 else ''}{int(_cashflow)}"
    except ValueError:
        return {
            'status': False,
            'tag': 'Invalid input for cash flow. Please enter numeric values.'
        }

    # Validate - Description
    if not is_valid_txt(_description):
        return {
            'status': False,
            'tag': f"Content text contains invalid characters. Please avoid using the following characters: {', '.join(invalid_characters)}."
        }

    # All validation passed -> Create file name to be created
    return {
        'status': True,
        'tag': '_'.join([_date, _branch, _cashflow, _description])
    }
