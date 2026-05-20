from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pyodbc
import getpass
import webbrowser
import threading
import uvicorn

# =========================
# SQL SERVER
# =========================

SERVER =
DATABASE =

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

STATUS_OPTIONS = [
    "New",
    "In Review",
    "Responded",
    "Closed",
    "Invalid",
    "Duplicate"
]

# =========================
# FASTAPI
# =========================

app = FastAPI(title="Onward Quote Intake Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# REQUEST MODEL
# =========================

class TrackingUpdate(BaseModel):
    quote_intake_id: int
    status: str
    notes: str = ""

# =========================
# DB CONNECTION
# =========================

def get_connection():
    return pyodbc.connect(CONN_STR)

# =========================
# FRONTEND UI
# =========================

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Onward Quote Intake Tracker</title>

<style>
body{
    margin:0;
    background:#F3F4F6;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial;
    color:#404040;
}

.hero{
    background:#3F3F46;
    color:white;
    padding:58px 72px;
}

.hero h1{
    margin:0;
    font-size:31px;
    font-weight:800;
    letter-spacing:1.6px;
}

.hero-sub{
    margin-top:14px;
    color:rgba(255,255,255,0.72);
    font-size:14px;
    font-weight:500;
}

.container{
    max-width:1380px;
    margin:-32px auto 70px auto;
    padding:0 35px;
}

.metrics{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:18px;
    margin-bottom:24px;
}

.metric-card{
    background:white;
    border-radius:18px;
    padding:24px;
    box-shadow:0 10px 30px rgba(0,0,0,0.05);
    border:1px solid #ECECEC;
}

.metric-label{
    font-size:12px;
    letter-spacing:1px;
    text-transform:uppercase;
    color:#8A8A8A;
}

.metric-value{
    margin-top:10px;
    font-size:32px;
    font-weight:800;
    color:#2F2F2F;
}

.filter-bar{
    position:sticky;
    top:18px;
    z-index:100;
    background:white;
    border-radius:18px;
    padding:22px;
    box-shadow:0 10px 30px rgba(0,0,0,0.05);
    border:1px solid #ECECEC;
    margin-bottom:24px;
}

.filter-grid{
    display:grid;
    grid-template-columns:2fr 1fr 160px;
    gap:14px;
}

input, select, textarea{
    width:100%;
    padding:12px;
    border-radius:10px;
    border:1px solid #DDD;
    background:#FAFAFA;
    font-size:14px;
    box-sizing:border-box;
}

button{
    background:#A7B4C7;
    color:white;
    border:none;
    border-radius:10px;
    padding:11px 16px;
    font-size:13px;
    cursor:pointer;
    font-weight:600;
}

button:hover{
    background:#97A6BB;
}

.list-card{
    background:white;
    border-radius:18px;
    overflow:hidden;
    box-shadow:0 10px 30px rgba(0,0,0,0.05);
    border:1px solid #ECECEC;
}

table{
    width:100%;
    border-collapse:collapse;
}

thead{
    background:#F8F8F9;
}

th{
    padding:18px 18px;
    font-size:12px;
    text-transform:uppercase;
    letter-spacing:1px;
    color:#7A7A7A;
    font-weight:700;
    text-align:left;
    border-bottom:1px solid #ECECEC;
}

td{
    padding:18px 18px;
    border-bottom:1px solid #F0F0F0;
    vertical-align:middle;
    font-size:14px;
}

tbody tr.main-row:hover{
    background:#FAFAFB;
}

.accent{
    width:4px;
    height:38px;
    border-radius:999px;
}

.new{ background:#9BAFD0; }
.review{ background:#D9C78F; }
.responded{ background:#9FB7A4; }
.closed{ background:#B8BCC4; }
.invalid{ background:#D3A6A6; }
.duplicate{ background:#B5A7CC; }

.name{
    font-weight:700;
    color:#2F2F2F;
}

.address, .date{
    color:#666;
}

.badge{
    display:inline-block;
    padding:7px 14px;
    border-radius:999px;
    font-size:12px;
    font-weight:700;
    border:1px solid rgba(0,0,0,0.06);
}

.badge-new{ background:#E7EDF6; color:#3F5577; }
.badge-review{ background:#EFE3B8; color:#6F5A1F; }
.badge-responded{ background:#DDE9DF; color:#4E6855; }
.badge-closed{ background:#F1F2F4; color:#6F7680; }
.badge-invalid{ background:#EACDCD; color:#815959; }
.badge-duplicate{ background:#D8D0E6; color:#65557D; }

.detail-row{
    display:none;
}

.detail-cell{
    background:#FCFCFD;
    padding:28px 36px;
}

.detail-grid{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:30px;
}

.section-title{
    font-size:12px;
    text-transform:uppercase;
    letter-spacing:1px;
    color:#8A8A8A;
    margin-bottom:10px;
}

.value{
    color:#404040;
    line-height:1.7;
    font-size:15px;
}

.notes{
    margin-top:24px;
    background:white;
    border-radius:12px;
    padding:16px;
    border:1px solid #ECECEC;
    line-height:1.6;
}

.history-toggle{
    margin-top:12px;
    color:#7D8CA3;
    font-size:13px;
    cursor:pointer;
    font-weight:600;
}

.history{
    display:none;
    margin-top:14px;
    padding-top:14px;
    border-top:1px solid #ECECEC;
}

.history-meta{
    color:#8A8A8A;
    font-size:12px;
    margin-bottom:4px;
}

.update{
    margin-top:28px;
    padding-top:24px;
    border-top:1px solid #ECECEC;
}

.update-title{
    font-size:13px;
    text-transform:uppercase;
    letter-spacing:1px;
    color:#7A7A7A;
    margin-bottom:14px;
}

textarea{
    min-height:90px;
    margin-top:12px;
    resize:vertical;
}

.loading{
    text-align:center;
    padding:80px;
    color:#777;
}

@media(max-width:1000px){
    .metrics{ grid-template-columns:1fr 1fr; }
    .filter-grid{ grid-template-columns:1fr; }
}
</style>
</head>

<body>

<div class="hero">
    <h1>ONWARD QUOTE INTAKE</h1>
    <div class="hero-sub">Homeowners Quote Intake & Workflow Management</div>
</div>

<div class="container">

    <div class="metrics">
        <div class="metric-card">
            <div class="metric-label">Total</div>
            <div class="metric-value" id="metric-total">0</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Active</div>
            <div class="metric-value" id="metric-active">0</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Closed</div>
            <div class="metric-value" id="metric-closed">0</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Excluded</div>
            <div class="metric-value" id="metric-excluded">0</div>
        </div>
    </div>

    <div class="filter-bar">
        <div class="filter-grid">
            <input id="search" placeholder="Search name, email, address..." oninput="renderList()">

            <select id="statusFilter" onchange="renderList()">
                <option value="">Active Only</option>
                <option>New</option>
                <option>In Review</option>
                <option>Responded</option>
                <option>Closed</option>
                <option>Invalid</option>
                <option>Duplicate</option>
            </select>

            <button onclick="loadInquiries()">Refresh</button>
        </div>
    </div>

    <div class="list-card">
        <table>
            <thead>
                <tr>
                    <th style="width:40px;"></th>
                    <th>Name</th>
                    <th>Address</th>
                    <th style="width:150px;">Received</th>
                    <th style="width:140px;">Status</th>
                    <th style="width:120px;"></th>
                </tr>
            </thead>
            <tbody id="list">
                <tr>
                    <td colspan="6" class="loading">Loading inquiries...</td>
                </tr>
            </tbody>
        </table>
    </div>

</div>

<script>
let inquiries = [];

function normalizeStatus(status){
    return (status || 'New').trim();
}

function getAccentClass(status){
    status = normalizeStatus(status);
    if(status === 'New') return 'new';
    if(status === 'In Review') return 'review';
    if(status === 'Responded') return 'responded';
    if(status === 'Closed') return 'closed';
    if(status === 'Invalid') return 'invalid';
    if(status === 'Duplicate') return 'duplicate';
    return 'new';
}

function getBadgeClass(status){
    status = normalizeStatus(status);
    if(status === 'New') return 'badge-new';
    if(status === 'In Review') return 'badge-review';
    if(status === 'Responded') return 'badge-responded';
    if(status === 'Closed') return 'badge-closed';
    if(status === 'Invalid') return 'badge-invalid';
    if(status === 'Duplicate') return 'badge-duplicate';
    return '';
}

function formatDate(value){
    if(!value) return '';
    return String(value).substring(0,10);
}

async function loadInquiries(){
    const response = await fetch('/inquiries');
    inquiries = await response.json();
    renderMetrics();
    renderList();
}

function renderMetrics(){
    document.getElementById('metric-total').innerText = inquiries.length;

    document.getElementById('metric-active').innerText =
        inquiries.filter(x =>
            ['New','In Review','Responded'].includes(normalizeStatus(x.CurrentStatus))
        ).length;

    document.getElementById('metric-closed').innerText =
        inquiries.filter(x => normalizeStatus(x.CurrentStatus) === 'Closed').length;

    document.getElementById('metric-excluded').innerText =
        inquiries.filter(x =>
            ['Invalid','Duplicate'].includes(normalizeStatus(x.CurrentStatus))
        ).length;
}

function renderList(){
    const search = document.getElementById('search').value.toLowerCase();
    const status = document.getElementById('statusFilter').value;

    let filtered = inquiries.filter(x => {
        const currentStatus = normalizeStatus(x.CurrentStatus);

        const combined = `
            ${x.FirstName || ''}
            ${x.LastName || ''}
            ${x.Email || ''}
            ${x.Address || ''}
            ${x.City || ''}
        `.toLowerCase();

        const matchesSearch = combined.includes(search);

        const matchesStatus = status
            ? currentStatus === status
            : !['Invalid','Duplicate'].includes(currentStatus);

        return matchesSearch && matchesStatus;
    });

    const list = document.getElementById('list');
    list.innerHTML = '';

    if(filtered.length === 0){
        list.innerHTML = "<tr><td colspan='6' class='loading'>No inquiries found.</td></tr>";
        return;
    }

    filtered.forEach(item => {
        const currentStatus = normalizeStatus(item.CurrentStatus);
        const accentClass = getAccentClass(currentStatus);
        const badgeClass = getBadgeClass(currentStatus);

        list.innerHTML += `
            <tr class="main-row">
                <td><div class="accent ${accentClass}"></div></td>
                <td class="name">${item.FirstName || ''} ${item.LastName || ''}</td>
                <td class="address">${item.Address || ''}, ${item.City || ''}, ${item.State || ''}</td>
                <td class="date">${formatDate(item.ReceivedTime)}</td>
                <td><span class="badge ${badgeClass}">${currentStatus}</span></td>
                <td><button onclick="toggleDetail(${item.Id})">View</button></td>
            </tr>

            <tr class="detail-row" id="detail-${item.Id}">
                <td colspan="6" class="detail-cell">
                    <div class="detail-grid">
                        <div>
                            <div class="section-title">Contact</div>
                            <div class="value">${item.Email || ''}<br>${item.Phone || ''}</div>
                        </div>

                        <div>
                            <div class="section-title">Last Updated</div>
                            <div class="value">${item.UpdatedBy || '-'}<br>${item.UpdatedAt || '-'}</div>
                        </div>
                    </div>

                    <div class="notes">
                        <b>Latest Note</b><br><br>
                        ${item.LatestNotes || 'No notes yet.'}

                        <div class="history-toggle" onclick="toggleHistory(${item.Id})">
                            View History
                        </div>

                        <div class="history" id="history-${item.Id}">
                            <div class="history-meta">${item.UpdatedAt || '-'} · ${item.UpdatedBy || '-'}</div>
                            ${item.LatestNotes || 'No history yet.'}
                        </div>
                    </div>

                    <div class="update">
                        <div class="update-title">Update Inquiry</div>

                        <select id="status-${item.Id}">
                            <option>New</option>
                            <option>In Review</option>
                            <option>Responded</option>
                            <option>Closed</option>
                            <option>Invalid</option>
                            <option>Duplicate</option>
                        </select>

                        <textarea id="notes-${item.Id}" placeholder="Add update notes..."></textarea>

                        <button onclick="saveUpdate(${item.Id})">Save Update</button>
                    </div>
                </td>
            </tr>
        `;
    });

    filtered.forEach(item => {
        const select = document.getElementById(`status-${item.Id}`);
        if(select){
            select.value = normalizeStatus(item.CurrentStatus);
        }
    });
}

function toggleDetail(id){
    const el = document.getElementById(`detail-${id}`);
    el.style.display = el.style.display === 'table-row' ? 'none' : 'table-row';
}

function toggleHistory(id){
    const el = document.getElementById(`history-${id}`);
    el.style.display = el.style.display === 'block' ? 'none' : 'block';
}

async function saveUpdate(id){
    const status = document.getElementById(`status-${id}`).value;
    const notes = document.getElementById(`notes-${id}`).value;

    await fetch('/tracking', {
        method:'POST',
        headers:{ 'Content-Type':'application/json' },
        body:JSON.stringify({
            quote_intake_id:id,
            status:status,
            notes:notes
        })
    });

    await loadInquiries();
}

loadInquiries();
setInterval(loadInquiries, 60000);
</script>

</body>
</html>
"""

# =========================
# GET INQUIRIES
# =========================

@app.get("/inquiries")
def get_inquiries():

    sql = """

    SELECT
        i.Id,
        i.ReceivedTime,
        i.FirstName,
        i.LastName,
        i.Email,
        i.Phone,
        i.Address,
        i.City,
        i.[State],

        latest.Status AS CurrentStatus,
        latest.Notes AS LatestNotes,
        latest.UpdatedBy,
        latest.UpdatedAt

    FROM dbo.OnwardQuoteIntake i

    OUTER APPLY (

        SELECT TOP 1
            t.Status,
            t.Notes,
            t.UpdatedBy,
            t.UpdatedAt

        FROM dbo.OnwardQuoteTracking t

        WHERE t.QuoteIntakeId = i.Id

        ORDER BY t.UpdatedAt DESC

    ) latest

    ORDER BY i.ReceivedTime DESC;

    """

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(sql)

    columns = [column[0] for column in cursor.description]

    rows = []

    for row in cursor.fetchall():

        item = dict(zip(columns, row))

        for key, value in item.items():

            if value is not None:
                item[key] = str(value)

        if not item.get("CurrentStatus"):
            item["CurrentStatus"] = "New"

        rows.append(item)

    cursor.close()
    conn.close()

    return rows

# =========================
# SAVE TRACKING
# =========================

@app.post("/tracking")
def insert_tracking(update: TrackingUpdate):

    sql = """

    INSERT INTO dbo.OnwardQuoteTracking
    (
        QuoteIntakeId,
        Status,
        Notes,
        UpdatedBy
    )

    VALUES (?, ?, ?, ?)

    """

    updated_by = getpass.getuser()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        sql,

        update.quote_intake_id,
        update.status,
        update.notes,
        updated_by

    )

    conn.commit()

    cursor.close()
    conn.close()

    return {"success": True}

# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    def open_browser():
        webbrowser.open("http://127.0.0.1:8001")

    threading.Timer(1.5, open_browser).start()

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_config=None
    )
