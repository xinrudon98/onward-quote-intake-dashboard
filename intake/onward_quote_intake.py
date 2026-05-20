import re
import win32com.client
import pyodbc


# =========================
# CONFIG
# =========================

SERVER = 
DATABASE = 
TABLE = "dbo.OnwardQuoteIntake"

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)


# =========================
# HELPERS
# =========================

def clean_text(value):

    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def safe_get(obj, attr, default=None):

    try:
        return getattr(obj, attr)

    except Exception:
        return default


def get_folder(parent, folder_name):

    for folder in parent.Folders:

        if folder.Name.strip().lower() == folder_name.lower():

            return folder

    raise Exception(f"Folder not found: {folder_name}")


def extract_field(body, label):

    pattern = rf"^{re.escape(label)}\s*:\s*(.+)$"

    match = re.search(
        pattern,
        body,
        flags=re.IGNORECASE | re.MULTILINE
    )

    return clean_text(match.group(1)) if match else None


def parse_from_line(body):

    match = re.search(
        r"^From:\s*(.*?)\s*<([^>]+)>",
        body,
        flags=re.IGNORECASE | re.MULTILINE
    )

    if match:

        return (
            clean_text(match.group(1)),
            clean_text(match.group(2))
        )

    return None, None


def parse_int(value):

    if not value:
        return None

    nums = re.findall(
        r"\d+",
        str(value).replace(",", "")
    )

    if not nums:
        return None

    return int("".join(nums))


def parse_estimated_value(value):

    if not value:
        return None, None

    nums = re.findall(r"\d[\d,]*", value)

    nums = [
        int(x.replace(",", ""))
        for x in nums
    ]

    if len(nums) >= 2:
        return nums[0], nums[1]

    if len(nums) == 1:
        return nums[0], None

    return None, None


def normalize_datetime(value):

    if value is None:
        return None

    try:
        return value.replace(tzinfo=None)

    except Exception:
        return value


def build_record(message):

    body = str(
        safe_get(message, "Body", "") or ""
    )

    from_name, from_email = parse_from_line(body)

    estimated_value_raw = extract_field(
        body,
        "Estimated Value"
    )

    estimated_value_min, estimated_value_max = parse_estimated_value(
        estimated_value_raw
    )

    return {

        "OutlookEntryID":
            clean_text(
                safe_get(message, "EntryID")
            ),

        "ReceivedTime":
            normalize_datetime(
                safe_get(message, "ReceivedTime")
            ),

        "FromName":
            from_name,

        "FromEmail":
            from_email,

        "UserType":
            extract_field(body, "User Type"),

        "State":
            extract_field(body, "State"),

        "Address":
            extract_field(body, "Address"),

        "City":
            extract_field(body, "City"),

        "Zip":
            extract_field(body, "ZIP"),

        "YearBuilt":
            parse_int(
                extract_field(body, "Year Built")
            ),

        "SqFt":
            parse_int(
                extract_field(body, "Area (sq ft)")
            ),

        "FirstName":
            extract_field(body, "First Name"),

        "LastName":
            extract_field(body, "Last Name"),

        "Email":
            extract_field(body, "Email"),

        "Phone":
            extract_field(body, "Phone"),

        "PreferredContact":
            extract_field(body, "Preferred Contact"),

        "EstimatedValueMin":
            estimated_value_min,

        "EstimatedValueMax":
            estimated_value_max,
    }


# =========================
# SQL INSERT
# =========================

def insert_record(cursor, record):

    sql = f"""
    IF NOT EXISTS (
        SELECT 1
        FROM {TABLE}
        WHERE OutlookEntryID = ?
    )
    BEGIN

        INSERT INTO {TABLE}
        (
            OutlookEntryID,
            ReceivedTime,
            FromName,
            FromEmail,
            UserType,
            [State],
            Address,
            City,
            Zip,
            YearBuilt,
            SqFt,
            FirstName,
            LastName,
            Email,
            Phone,
            PreferredContact,
            EstimatedValueMin,
            EstimatedValueMax
        )

        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?
        )

    END
    """

    params = [

        # IF NOT EXISTS
        record["OutlookEntryID"],

        # INSERT VALUES
        record["OutlookEntryID"],
        record["ReceivedTime"],
        record["FromName"],
        record["FromEmail"],
        record["UserType"],
        record["State"],
        record["Address"],
        record["City"],
        record["Zip"],
        record["YearBuilt"],
        record["SqFt"],
        record["FirstName"],
        record["LastName"],
        record["Email"],
        record["Phone"],
        record["PreferredContact"],
        record["EstimatedValueMin"],
        record["EstimatedValueMax"],
    ]

    cursor.execute(sql, params)


# =========================
# MAIN
# =========================

def main():

    print("STARTING SCRIPT...")

    outlook = win32com.client.Dispatch(
        "Outlook.Application"
    )

    namespace = outlook.GetNamespace("MAPI")

    inbox = namespace.GetDefaultFolder(6)

    onward_folder = get_folder(
        inbox,
        "ONWARD"
    )

    homeowners_folder = get_folder(
        onward_folder,
        "HOMEOWNERS"
    )

    print(
        "HOMEOWNERS ITEMS:",
        homeowners_folder.Items.Count
    )

    items = homeowners_folder.Items

    items.Sort("[ReceivedTime]", True)

    conn = pyodbc.connect(CONN_STR)

    cursor = conn.cursor()

    checked_count = 0
    matched_count = 0
    insert_attempts = 0

    for message in items:

        try:

            # Only MailItem
            if safe_get(message, "Class") != 43:
                continue

            checked_count += 1

            sender_name = str(
                safe_get(message, "SenderName", "") or ""
            )

            if sender_name != "noreply@onwardins.com":
                continue

            matched_count += 1

            print(
                "MATCH FOUND:",
                safe_get(message, "Subject", "")
            )

            record = build_record(message)

            if not record["OutlookEntryID"]:
                continue

            insert_record(cursor, record)

            insert_attempts += 1

        except Exception as e:

            print("ERROR:", e)

    conn.commit()

    cursor.close()

    conn.close()

    print("\nDone.")

    print(
        f"Checked emails: {checked_count}"
    )

    print(
        f"Matched emails: {matched_count}"
    )

    print(
        f"Insert attempts: {insert_attempts}"
    )

    print(
        f"Table: {DATABASE}.{TABLE}"
    )


if __name__ == "__main__":

    main()
