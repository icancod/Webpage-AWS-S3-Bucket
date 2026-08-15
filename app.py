
import json
import os
import time
import boto3
import streamlit as st


st.set_page_config(page_title="S3 Manager", page_icon="☁", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
        .main .block-container {
            padding-top: 0.25rem;
            padding-bottom: 0.75rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1120 0%, #10192d 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        [data-testid="stSidebar"] * {
            color: #f8fafc;
        }
        section[data-testid="stSidebar"] [data-testid="stButton"] button {
            width: 100%;
            border-radius: 14px;
            padding: 0.65rem 0.85rem;
            border: 1px solid transparent;
            background: transparent;
            color: #cbd5e1;
            text-align: left;
            box-shadow: none;
            min-height: 2.7rem;
        }
        section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
            background: rgba(59, 130, 246, 0.18);
            border-color: rgba(59, 130, 246, 0.35);
            color: #eff6ff;
        }
        section[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(255, 255, 255, 0.08);
        }
        .sidebar-shell {
            padding: 0.35rem 0.15rem 0.65rem;
        }
        .sidebar-brand {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
            padding: 0.5rem 0.15rem 0.8rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 0.8rem;
        }
        .sidebar-brand-title {
            font-size: 1rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #f8fafc;
        }
        .sidebar-brand-subtitle {
            font-size: 0.82rem;
            color: #94a3b8;
            line-height: 1.35;
        }
        .nav-group {
            margin-top: 0.65rem;
        }
        .nav-group-label {
            color: #94a3b8;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin: 0 0 0.35rem;
            padding: 0 0.15rem;
        }
        .nav-divider {
            height: 1px;
            background: rgba(255, 255, 255, 0.08);
            margin: 0.85rem 0;
        }
        .sidebar-status {
            margin-top: 0.9rem;
            padding-top: 0.85rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }
        .stApp {
            background: linear-gradient(135deg, #080d18 0%, #0b1120 46%, #111827 100%);
            color: #e5eefc;
        }
        .login-shell {
            min-height: auto;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding: 0;
            margin-top: -0.5rem;
        }
        .login-card {
            width: min(420px, 100%);
            padding: 1.1rem;
            border-radius: 22px;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: 0 18px 42px rgba(2, 6, 23, 0.32);
            backdrop-filter: blur(18px);
            position: relative;
            overflow: hidden;
        }
        .login-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.34rem 0.68rem;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.12);
            color: #bfdbfe;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }
        .login-title {
            margin: 0.8rem 0 0;
            font-size: clamp(1.65rem, 2.2vw, 2rem);
            line-height: 1.05;
            letter-spacing: -0.04em;
            color: #f8fafc;
        }
        .login-subtitle {
            margin: 0.55rem 0 0;
            color: #cbd5e1;
            line-height: 1.55;
            max-width: 34rem;
            font-size: 0.92rem;
        }
        .login-note {
            margin-top: 0.8rem;
            padding: 0.72rem 0.9rem;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(148, 163, 184, 0.14);
            color: #cbd5e1;
            font-size: 0.84rem;
        }
        .login-card-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.8rem;
            margin-bottom: 0.25rem;
        }
        .login-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.32rem 0.62rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.06);
            color: #e2e8f0;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .login-card-pill {
            color: #86efac;
            font-size: 0.78rem;
            font-weight: 600;
        }
        .login-form-title {
            margin: 0 0 0.2rem;
            color: #f8fafc;
            font-size: 1.1rem;
            font-weight: 700;
        }
        .login-footnote {
            margin-top: 0.65rem;
            color: #94a3b8;
            font-size: 0.76rem;
        }
        .login-form-shell {
            margin-top: 0.9rem;
        }
        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 0.3rem;
        }
        .section-subtitle {
            color: #94a3b8;
            margin-bottom: 0.85rem;
        }
        .shell-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            margin: 0.4rem 0 1rem;
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: rgba(17, 24, 39, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 24px rgba(2, 6, 23, 0.22);
        }
        .shell-kicker {
            color: #3b82f6;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }
        .shell-title {
            margin: 0.2rem 0 0;
            color: #f8fafc;
            font-size: clamp(1.35rem, 2vw, 1.75rem);
            line-height: 1.1;
        }
        .shell-subtitle {
            margin: 0.35rem 0 0;
            color: #94a3b8;
            max-width: 48rem;
        }
        .shell-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .shell-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.4rem 0.7rem;
            border-radius: 999px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.04);
            color: #e2e8f0;
            font-size: 0.8rem;
        }
        [data-testid="stMetricValue"] {
            color: #f8fafc;
        }
        [data-testid="stMetric"] {
            background: rgba(17, 24, 39, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 24px rgba(2, 6, 23, 0.22);
            border-radius: 16px;
            padding: 0.85rem 0.95rem;
        }
        [data-testid="stMetricLabel"] {
            color: #94a3b8;
            font-weight: 700;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        }
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background: rgba(15, 23, 42, 0.6);
        }
        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 14px !important;
            min-height: 3.1rem;
        }
        .stTextInput input {
            background: rgba(15, 23, 42, 0.78) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(148, 163, 184, 0.2) !important;
        }
        .stTextInput input::placeholder {
            color: #94a3b8 !important;
        }
        .stTextInput input:focus {
            border-color: rgba(96, 165, 250, 0.8) !important;
            box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.2) !important;
        }
        .stSelectbox label,
        .stTextInput label,
        .stTextArea label,
        .stFileUploader label,
        .stRadio label {
            color: #cbd5e1 !important;
            font-weight: 600 !important;
        }
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 14px !important;
            background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%) !important;
            color: #eff6ff !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 14px 30px rgba(37, 99, 235, 0.35) !important;
            min-height: 3.2rem;
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            filter: brightness(1.04);
            transform: translateY(-1px);
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.5rem 0.8rem;
            border-radius: 999px;
            background: rgba(16, 185, 129, 0.14);
            color: #6ee7b7;
            font-weight: 700;
            font-size: 0.9rem;
        }
        .panel {
            padding: 1rem 1.05rem;
            border-radius: 18px;
            background: rgba(17, 24, 39, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 20px rgba(2, 6, 23, 0.18);
            margin-bottom: 0.85rem;
        }
        .hero-card {
            padding: 1.3rem 1.4rem;
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.96), rgba(15, 23, 42, 0.92));
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 18px 50px rgba(2, 6, 23, 0.25);
            margin-bottom: 0.9rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }
        .hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.45rem 0.7rem;
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(14, 165, 233, 0.12));
            color: #93c5fd;
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .hero-title {
            margin: 0.45rem 0 0.25rem;
            font-size: clamp(1.6rem, 2.15vw, 2.2rem);
            color: #f8fafc;
            line-height: 1.05;
        }
        .hero-subtitle {
            margin: 0;
            color: #94a3b8;
            font-size: 0.98rem;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.55rem 0.85rem;
            border-radius: 999px;
            background: rgba(16, 185, 129, 0.14);
            color: #6ee7b7;
            font-weight: 700;
            font-size: 0.9rem;
            white-space: nowrap;
        }
        .stAlert {
            border-radius: 16px;
        }
        [data-testid="stFileUploader"] {
            margin-top: 0.35rem;
        }
        [data-testid="stFileUploader"] section,
        [data-testid="stFileUploaderDropzone"] {
            background: rgba(15, 23, 42, 0.72) !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            border-radius: 18px !important;
            min-height: 132px !important;
        }
        [data-testid="stFileUploaderDropzone"] > div {
            padding: 1rem !important;
        }
        [data-testid="stFileUploaderDropzone"] label,
        [data-testid="stFileUploader"] label {
            color: #e2e8f0 !important;
        }
        [data-testid="stFileUploader"] button {
            border-radius: 999px !important;
        }
        .compact-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.85rem;
        }
        @media (max-width: 900px) {
            .compact-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def append_log(message: str) -> None:
    if "logs" not in st.session_state:
        st.session_state.logs = []
    st.session_state.logs.append(message)

    audit_event = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "message": message,
    }
    if "audit_events" not in st.session_state:
        st.session_state.audit_events = []
    st.session_state.audit_events.append(audit_event)

    try:
        with open("cloudops_audit_log.json", "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(audit_event) + "\n")
    except Exception:
        pass

    dynamodb_client = getattr(st.session_state, "dynamodb_client", None)
    if dynamodb_client:
        try:
            table_name = "cloudops-audit-log"
            try:
                dynamodb_client.describe_table(TableName=table_name)
            except dynamodb_client.exceptions.ResourceNotFoundException:
                dynamodb_client.create_table(
                    TableName=table_name,
                    KeySchema=[{"AttributeName": "event_id", "KeyType": "HASH"}],
                    AttributeDefinitions=[{"AttributeName": "event_id", "AttributeType": "S"}],
                    ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                )
                dynamodb_client.get_waiter("table_exists").wait(TableName=table_name)
            dynamodb_client.put_item(
                TableName=table_name,
                Item={
                    "event_id": {"S": f"{int(time.time() * 1000)}-{len(st.session_state.audit_events)}"},
                    "timestamp": {"S": audit_event["timestamp"]},
                    "message": {"S": message},
                    "region": {"S": st.session_state.connected_region or "unknown"},
                },
            )
        except Exception:
            pass


def load_audit_events():
    if "audit_events" in st.session_state:
        return st.session_state.audit_events

    events = []
    try:
        with open("cloudops_audit_log.json", "r", encoding="utf-8") as log_file:
            for line in log_file:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except FileNotFoundError:
        pass

    st.session_state.audit_events = events
    return events


def safe_tag_value(tags, key):
    if not tags:
        return "N/A"
    for tag in tags:
        if tag.get("Key") == key:
            return tag.get("Value", "N/A")
    return "N/A"


if "client" not in st.session_state:
    st.session_state.client = None
if "logs" not in st.session_state:
    st.session_state.logs = []
if "audit_events" not in st.session_state:
    st.session_state.audit_events = []
if "connected_region" not in st.session_state:
    st.session_state.connected_region = None
if "ec2_client" not in st.session_state:
    st.session_state.ec2_client = None
if "cloudwatch_client" not in st.session_state:
    st.session_state.cloudwatch_client = None
if "lambda_client" not in st.session_state:
    st.session_state.lambda_client = None
if "iam_client" not in st.session_state:
    st.session_state.iam_client = None
if "dynamodb_client" not in st.session_state:
    st.session_state.dynamodb_client = None
if "sns_client" not in st.session_state:
    st.session_state.sns_client = None
if "elbv2_client" not in st.session_state:
    st.session_state.elbv2_client = None
if "autoscaling_client" not in st.session_state:
    st.session_state.autoscaling_client = None
if "cloudtrail_client" not in st.session_state:
    st.session_state.cloudtrail_client = None
if "active_section" not in st.session_state:
    st.session_state.active_section = "Overview"


def set_active_section(section: str) -> None:
    st.session_state.active_section = section


NAV_GROUPS = [
    (
        "Storage",
        [
            ("◦ Overview", "Overview"),
            ("◦ Create Bucket", "Create Bucket"),
            ("◦ Upload Files", "Upload Files"),
            ("◦ Access Control", "Manage Access"),
        ],
    ),
    (
        "Compute",
        [
            ("◦ EC2 Instances", "Question 4 - EC2"),
            ("◦ Launch EC2", "Step 5 - Launch EC2"),
        ],
    ),
    (
        "Monitoring",
        [
            ("◦ Monitoring", "Monitoring"),
            ("◦ CloudWatch Alerts", "CloudWatch Alerts"),
            ("◦ Lambda", "Lambda"),
        ],
    ),
    (
        "Network & Security",
        [
            ("◦ Network", "Network"),
            ("◦ Security", "Security"),
            ("◦ Audit", "Audit"),
            ("◦ Security & Compliance", "Security & Compliance"),
        ],
    ),
    (
        "High Availability & Scaling",
        [
            ("◦ HA & Scaling", "High Availability & Scaling"),
            ("◦ Architecture Overview", "Architecture Overview"),
            ("◦ CIA-3 Validation", "CIA-3 Validation"),
        ],
    ),
    (
        "Reliability & Cost",
        [
            ("◦ Reliability & Recovery", "Reliability & Recovery"),
            ("◦ Cost Optimization", "Cost Optimization"),
        ],
    ),
    (
        "Reporting",
        [
            ("◦ Resource Report", "Question 5 - Report"),
            ("◦ Extended Report", "Extended Report"),
            ("◦ Activity Logs", "Activity Logs"),
        ],
    ),
]

PAGE_META = {
    "Overview": ("Cloud Infrastructure", "Overview", "Manage your AWS storage and compute resources from one workspace."),
    "Create Bucket": ("Storage", "Create Bucket", "Create a new S3 bucket with the existing AWS workflow."),
    "Upload Files": ("Storage", "Upload Files", "Upload files into your chosen S3 folder."),
    "Manage Access": ("Storage", "Access Control", "Adjust object ACLs for the selected bucket."),
    "Question 4 - EC2": ("Compute", "EC2 Instances", "Review running EC2 instances in the connected region."),
    "Step 5 - Launch EC2": ("Compute", "Launch EC2", "Launch a new EC2 instance using the existing launch flow."),
    "Monitoring": ("Monitoring", "Monitoring", "Review CloudWatch health, metrics, and resource signals from the connected AWS account."),
    "CloudWatch Alerts": ("Monitoring", "CloudWatch Alerts", "List, create, and confirm deletion of CloudWatch alarms."),
    "Lambda": ("Monitoring", "Lambda", "Review Lambda functions and invoke a selected function with explicit confirmation."),
    "Network": ("Network & Security", "Network", "Inspect VPC, subnet, routing, and internet connectivity resources."),
    "Security": ("Network & Security", "Security", "Review IAM identities and security-related AWS resources."),
    "Audit": ("Network & Security", "Audit", "Review the local and optional DynamoDB audit trail for this session."),
    "Security & Compliance": ("Network & Security", "Security & Compliance", "Review AWS security posture, encryption, and configuration compliance checks."),
    "High Availability & Scaling": ("High Availability & Scaling", "High Availability & Scaling", "Review ALBs, target groups, launch templates, and Auto Scaling resources."),
    "Architecture Overview": ("High Availability & Scaling", "Architecture Overview", "Visualize the cloud architecture with VPC, ALB, ASG, and backend services."),
    "CIA-3 Validation": ("High Availability & Scaling", "CIA-3 Validation", "Check the current AWS environment against the scalability, HA, and security rubric."),
    "Reliability & Recovery": ("Reliability & Cost", "Reliability & Recovery", "Assess multi-AZ, backup, failover, and recovery capability."),
    "Cost Optimization": ("Reliability & Cost", "Cost Optimization", "Summarize AWS resources suitable for a pricing-calculator estimate and best-practice recommendations."),
    "Question 5 - Report": ("Reporting", "Resource Report", "Generate and upload an AWS resource report to S3."),
    "Extended Report": ("Reporting", "Extended Report", "Generate a broader resource report covering S3, EC2, monitoring, network, security, and audit data."),
    "Activity Logs": ("Reporting", "Activity Logs", "Review the recent actions from this session."),
}

with st.sidebar:
    st.markdown(
        """
        <div class='sidebar-shell'>
            <div class='sidebar-brand'>
                <div class='sidebar-brand-title'>CloudOps Console</div>
                <div class='sidebar-brand-subtitle'>AWS Resource Manager</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.client:
        for group_label, items in NAV_GROUPS:
            st.markdown(f"<div class='nav-group-label'>{group_label}</div>", unsafe_allow_html=True)
            for display_label, section_key in items:
                st.button(
                    display_label,
                    key=f"nav_{section_key}",
                    type="primary" if st.session_state.active_section == section_key else "secondary",
                    use_container_width=True,
                    on_click=set_active_section,
                    args=(section_key,),
                )
            st.markdown("<div class='nav-divider'></div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class='sidebar-status'>
                <span class='status-badge'>● Connected</span>
                <div style='margin-top:0.45rem;color:#94a3b8;font-size:0.85rem;'>Region: {st.session_state.connected_region or 'unknown'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Disconnect", use_container_width=True):
            st.session_state.client = None
            st.session_state.connected_region = None
            st.session_state.ec2_client = None
            st.session_state.cloudwatch_client = None
            st.session_state.lambda_client = None
            st.session_state.iam_client = None
            st.session_state.dynamodb_client = None
            st.session_state.sns_client = None
            st.session_state.elbv2_client = None
            st.session_state.autoscaling_client = None
            st.session_state.cloudtrail_client = None
            st.session_state.active_section = "Overview"
            append_log("Disconnected from AWS")
            st.rerun()


client = st.session_state.client
ec2_client = st.session_state.ec2_client
cloudwatch_client = st.session_state.cloudwatch_client
lambda_client = st.session_state.lambda_client
iam_client = st.session_state.iam_client
dynamodb_client = st.session_state.dynamodb_client
sns_client = st.session_state.sns_client
elbv2_client = st.session_state.elbv2_client
autoscaling_client = st.session_state.autoscaling_client
cloudtrail_client = st.session_state.cloudtrail_client

if not client:
    st.markdown("<div class='login-shell'>", unsafe_allow_html=True)
    center_col = st.columns([1.15, 1.7, 1.15], gap="large")[1]

    with center_col:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<span class='login-badge'>AWS S3 access</span>", unsafe_allow_html=True)
        st.markdown("<h2 class='login-title'>Connect to AWS</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p class='login-subtitle'>Sign in with your AWS credentials to open the dashboard and manage your S3 resources.</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='login-separator'></div>", unsafe_allow_html=True)
        st.markdown("<div class='login-form-shell'>", unsafe_allow_html=True)
        with st.form("aws_connect_form", clear_on_submit=False):
            ak = st.text_input("Access Key", placeholder="AKIAxxxxxxxxxxxxxxxx", type="password")
            sk = st.text_input("Secret Key", placeholder="Paste your secret access key", type="password")
            tk = st.text_input("Session Token", placeholder="Optional: temporary session token", type="password")
            region = st.selectbox("Region", ["us-east-1", "ap-south-1", "us-west-1"])
            submitted = st.form_submit_button("Connect to AWS", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-note'>Your credentials are used only for this session.</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-footnote'>No bucket data is loaded until you connect successfully.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        try:
            session_token = tk.strip() if tk else None
            client = boto3.client(
                "s3",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=session_token,
                region_name=region,
            )
            ec2_client = boto3.client(
                "ec2",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=session_token,
                region_name=region,
            )
            cloudwatch_client = boto3.client(
                "cloudwatch",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=session_token,
                region_name=region,
            )
            lambda_client = boto3.client(
                "lambda",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=session_token,
                region_name=region,
            )
            iam_client = boto3.client(
                "iam",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=session_token,
            )
            dynamodb_client = boto3.client(
                "dynamodb",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=session_token,
                region_name=region,
            )
            sns_client = boto3.client(
                "sns",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=session_token,
                region_name=region,
            )
            elbv2_client = boto3.client(
                "elbv2",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=session_token,
                region_name=region,
            )
            autoscaling_client = boto3.client(
                "autoscaling",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=session_token,
                region_name=region,
            )
            cloudtrail_client = boto3.client(
                "cloudtrail",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=session_token,
                region_name=region,
            )
            client.list_buckets()
            st.session_state.client = client
            st.session_state.ec2_client = ec2_client
            st.session_state.cloudwatch_client = cloudwatch_client
            st.session_state.lambda_client = lambda_client
            st.session_state.iam_client = iam_client
            st.session_state.dynamodb_client = dynamodb_client
            st.session_state.sns_client = sns_client
            st.session_state.elbv2_client = elbv2_client
            st.session_state.autoscaling_client = autoscaling_client
            st.session_state.cloudtrail_client = cloudtrail_client
            st.session_state.connected_region = region

            append_log(f"Connected to AWS in {region}")
            st.rerun()
        except Exception as e:
            st.error(str(e))
    st.markdown("</div>", unsafe_allow_html=True)
else:
    try:
        bucket_response = client.list_buckets()
        buckets = bucket_response.get("Buckets", [])
    except Exception as e:
        st.error(f"Connection lost: {e}")
        st.stop()

    bucket_names = [bucket["Name"] for bucket in buckets]
    total_buckets = len(bucket_names)
    total_objects = 0
    for bucket_name in bucket_names[:5]:
        try:
            total_objects += len(client.list_objects_v2(Bucket=bucket_name).get("Contents", []))
        except Exception:
            continue

    st.markdown(
        f"""
        <div class='shell-header'>
            <div>
                <div class='shell-kicker'>{PAGE_META[st.session_state.active_section][0]}</div>
                <h1 class='shell-title'>{PAGE_META[st.session_state.active_section][1]}</h1>
                <p class='shell-subtitle'>{PAGE_META[st.session_state.active_section][2]}</p>
            </div>
            <div class='shell-chips'>
                <span class='shell-chip'>Region: {st.session_state.connected_region or 'unknown'}</span>
                <span class='shell-chip'>AWS session active</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("S3 Buckets", total_buckets)
    metric_col2.metric("Objects", total_objects)
    metric_col3.metric("AWS Region", st.session_state.connected_region or "unknown")
    metric_col4.metric("Activity Events", len(st.session_state.logs))

    active_section = st.session_state.active_section

    if active_section == "Overview":
        overview_col1, overview_col2 = st.columns([1.25, 0.75])
        with overview_col1:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>S3 Buckets</div>", unsafe_allow_html=True)
            st.markdown("<div class='section-subtitle'>Your current bucket inventory.</div>", unsafe_allow_html=True)
            if bucket_names:
                for bucket_name in bucket_names:
                    st.write(f"• {bucket_name}")
            else:
                st.info("No buckets found yet.")
            st.markdown("</div>", unsafe_allow_html=True)
        with overview_col2:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Quick Actions</div>", unsafe_allow_html=True)
            st.markdown("<div class='section-subtitle'>Jump to common workflows.</div>", unsafe_allow_html=True)
            if st.button("Create Bucket", use_container_width=True, key="quick_create"):
                set_active_section("Create Bucket")
                st.rerun()
            if st.button("Upload Files", use_container_width=True, key="quick_upload"):
                set_active_section("Upload Files")
                st.rerun()
            if st.button("Manage Access", use_container_width=True, key="quick_access"):
                set_active_section("Manage Access")
                st.rerun()
            if st.button("Launch EC2", use_container_width=True, key="quick_launch"):
                set_active_section("Step 5 - Launch EC2")
                st.rerun()
            if st.button("Generate Report", use_container_width=True, key="quick_report"):
                set_active_section("Question 5 - Report")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Recent Activity</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Recent actions are preserved for the current session.</div>", unsafe_allow_html=True)
        if st.session_state.logs:
            for log_entry in reversed(st.session_state.logs):
                st.write(f"• {log_entry}")
        else:
            st.info("No activity yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Create Bucket":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Create a bucket</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Choose a name and region, then create a new bucket with one action.</div>", unsafe_allow_html=True)
        with st.form("create_bucket_form"):
            bucket = st.text_input("Bucket Name", placeholder="my-new-bucket")
            reg = st.selectbox("Bucket Region", ["us-east-1", "ap-south-1"])
            create_submitted = st.form_submit_button("Create Bucket", use_container_width=True)

        if create_submitted:
            try:
                if not bucket:
                    st.warning("Enter a bucket name first.")
                elif reg == "us-east-1":
                    client.create_bucket(Bucket=bucket)
                    st.success("Bucket created")
                    append_log(f"Created bucket {bucket}")
                    st.rerun()
                else:
                    client.create_bucket(
                        Bucket=bucket,
                        CreateBucketConfiguration={"LocationConstraint": reg},
                    )
                    st.success("Bucket created")
                    append_log(f"Created bucket {bucket}")
                    st.rerun()
            except Exception as e:
                st.error(str(e))
        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Upload Files":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Upload files</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Upload files into a folder inside the selected bucket.</div>", unsafe_allow_html=True)

        if not bucket_names:
            st.info("Create a bucket first to enable uploads.")
        else:
            with st.form("upload_form"):
                upload_top_left, upload_top_right = st.columns(2)
                with upload_top_left:
                    selected_bucket = st.selectbox(
                        "Select Bucket",
                        bucket_names,
                        key="upload_bucket"
                    )

                with upload_top_right:
                    selected_folder = st.selectbox(
                        "Select Folder",
                        ["ufolder", "efolder"]
                    )

                files = st.file_uploader(
                    "Upload Files",
                    accept_multiple_files=True
                )

                upload_submitted = st.form_submit_button(
                    "Upload",
                    use_container_width=True
                )

            if upload_submitted:
                if not files:
                    st.warning("Choose at least one file.")
                else:
                    try:
                        client.put_object(Bucket=selected_bucket, Key="ufolder/")
                        client.put_object(Bucket=selected_bucket, Key="efolder/")

                        for file_obj in files:
                            s3_key = f"{selected_folder}/{file_obj.name}"

                            client.upload_fileobj(
                                file_obj,
                                selected_bucket,
                                s3_key
                            )

                            append_log(
                                f"Uploaded {file_obj.name} to {selected_bucket}/{selected_folder}"
                            )

                        st.success("✅ File uploaded successfully!")

                        st.subheader("Objects Stored in Bucket")

                        response = client.list_objects_v2(
                            Bucket=selected_bucket
                        )

                        if "Contents" in response:
                            for obj in response["Contents"]:
                                st.write(f"📄 {obj['Key']}")
                        else:
                            st.info("Bucket is empty.")

                        append_log(
                            f"Displayed objects in bucket {selected_bucket}"
                        )

                    except Exception as e:
                        st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Manage Access":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Manage access</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Adjust the ACL of a specific object only after selecting a bucket.</div>", unsafe_allow_html=True)

        if not bucket_names:
            st.info("No buckets available.")
        else:
            with st.form("acl_form"):
                bucket_for_acl = st.selectbox("Bucket", bucket_names, key="acl_bucket")
                try:
                    objs = client.list_objects_v2(Bucket=bucket_for_acl)
                    keys = [obj["Key"] for obj in objs.get("Contents", [])]
                except Exception as e:
                    st.error(str(e))
                    keys = []

                if keys:
                    obj = st.selectbox("Object", keys)
                    acl = st.selectbox("Access", ["private", "public-read", "authenticated-read"])
                    acl_submitted = st.form_submit_button("Apply ACL", use_container_width=True)
                else:
                    st.info("No objects found in this bucket.")
                    acl_submitted = False

            if acl_submitted:
                try:
                    client.put_object_acl(Bucket=bucket_for_acl, Key=obj, ACL=acl)
                    st.success("ACL updated")
                    append_log(f"Changed ACL of {obj} to {acl}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Question 4 - EC2":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>EC2 Instances</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Retrieve all running EC2 instances.</div>", unsafe_allow_html=True)

        if st.button("Fetch Running EC2 Instances"):
            try:
                response = ec2_client.describe_instances()
                found = False

                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        if instance["State"]["Name"] == "running":
                            found = True

                            instance_id = instance["InstanceId"]
                            instance_type = instance["InstanceType"]
                            state = instance["State"]["Name"]
                            public_ip = instance.get("PublicIpAddress", "N/A")
                            az = instance["Placement"]["AvailabilityZone"]

                            name = "N/A"
                            if "Tags" in instance:
                                for tag in instance["Tags"]:
                                    if tag["Key"] == "Name":
                                        name = tag["Value"]

                            st.write("Instance ID:", instance_id)
                            st.write("Instance Name:", name)
                            st.write("Instance Type:", instance_type)
                            st.write("Instance State:", state)
                            st.write("Public IPv4:", public_ip)
                            st.write("Availability Zone:", az)
                            st.write("---")

                if not found:
                    st.info("No running EC2 instances found.")

            except Exception as e:
                st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Step 5 - Launch EC2":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Launch EC2 Instance</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Launch a new EC2 instance with configurable settings.</div>", unsafe_allow_html=True)

        if not st.session_state.ec2_client:
            st.info("Connect to AWS first to enable EC2 launch functionality.")
        else:
            existing_key_pairs = []
            sshes = []
            vpcs = []
            subnets = []
            default_amis = {}

            with st.spinner("Fetching AWS resources..."):
                try:
                    kp_response = ec2_client.describe_key_pairs()
                    existing_key_pairs = [kp["KeyName"] for kp in kp_response.get("KeyPairs", [])]
                except Exception:
                    st.warning("Could not fetch key pairs")

                try:
                    sg_response = ec2_client.describe_security_groups()
                    sshes = [sg["GroupName"] for sg in sg_response.get("SecurityGroups", [])]
                except Exception:
                    st.warning("Could not fetch security groups")

                try:
                    vpc_response = ec2_client.describe_vpcs()
                    vpcs = [{"VpcId": v["VpcId"], "Name": v.get("Tags", [{}])[0].get("Value", v["VpcId"])}
                            for v in vpc_response.get("Vpcs", [])]
                except Exception:
                    st.warning("Could not fetch VPCs")

                try:
                    subnet_response = ec2_client.describe_subnets()
                    subnets = [{"SubnetId": s["SubnetId"], "Name": s.get("Tags", [{}])[0].get("Value", s["SubnetId"]),
                               "AvailabilityZone": s.get("AvailabilityZone", "N/A")}
                               for s in subnet_response.get("Subnets", [])]
                except Exception:
                    st.warning("Could not fetch subnets")

                default_amis = {
                    "us-east-1": {"Amazon Linux 2": "ami-0c02fb55956c7d316", "Ubuntu 22.04": "ami-0dba2cb6798deb6d8", "Ubuntu 20.04": "ami-042e6666616abcaa9"},
                    "ap-south-1": {"Amazon Linux 2": "ami-05a6b4b3204e9cbd3", "Ubuntu 22.04": "ami-0b8017d10ab5f6baf", "Ubuntu 20.04": "ami-03b9a3b8d6e1a2c9d"},
                    "us-west-1": {"Amazon Linux 2": "ami-03ab395eeda6485d1", "Ubuntu 22.04": "ami-0a888888888888888", "Ubuntu 20.04": "ami-0e888888888888888"}
                }

            region = st.session_state.connected_region
            ami_options = ["<Select AMI>"]
            if region in default_amis:
                for name, ami_id in default_amis[region].items():
                    ami_options.append(f"{name} ({ami_id})")

            with st.form("launch_ec2_form"):
                st.markdown("<div class='nav-group-label'>01 — Instance</div>", unsafe_allow_html=True)
                instance_name = st.text_input(
                    "Instance Name (for AWS console tag)",
                    placeholder="my-ec2-instance",
                    key="launch_instance_name"
                )

                st.markdown("<div class='nav-group-label'>02 — Image</div>", unsafe_allow_html=True)
                selected_ami_display = st.selectbox(
                    "Choose AMI",
                    ami_options,
                    key="launch_ami_select"
                )

                ami_id = ""
                if selected_ami_display != "<Select AMI>":
                    ami_id = selected_ami_display.split("(")[-1].rstrip(")")

                st.markdown("<div class='nav-group-label'>03 — Compute</div>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    instance_type = st.selectbox(
                        "Instance Type",
                        ["t2.micro", "t3.micro", "t2.small", "t3.small", "t3.medium"],
                        key="launch_instance_type"
                    )
                with col2:
                    key_name_options = ["<No key pair>"] + existing_key_pairs
                    key_name = st.selectbox(
                        "Key Pair (existing)",
                        key_name_options,
                        key="launch_key_name_select"
                    )
                    key_name = None if key_name == "<No key pair>" else key_name

                st.markdown("<div class='nav-group-label'>04 — Network</div>", unsafe_allow_html=True)
                net_col1, net_col2 = st.columns(2)
                with net_col1:
                    vpc_options = ["<Default VPC>"]
                    for vpc in vpcs:
                        vpc_options.append(f"{vpc['Name']} ({vpc['VpcId']})")
                    selected_vpc = st.selectbox(
                        "VPC",
                        vpc_options,
                        key="launch_vpc"
                    )
                with net_col2:
                    subnet_options = ["<Default Subnet>"]
                    for subnet in subnets:
                        subnet_options.append(f"{subnet['Name']} - {subnet['AvailabilityZone']} ({subnet['SubnetId']})")
                    selected_subnet = st.selectbox(
                        "Subnet",
                        subnet_options,
                        key="launch_subnet"
                    )

                st.markdown("<div class='nav-group-label'>05 — Security</div>", unsafe_allow_html=True)
                sg_option = st.radio(
                    "Choose security group option",
                    ["Use existing security group", "Create new with default rules"],
                    key="sg_option"
                )

                existing_sg_name = None
                if sg_option == "Use existing security group":
                    sg_options = ["<Select Security Group>"] + sshes
                    selected_sg = st.selectbox(
                        "Security Group",
                        sg_options,
                        key="launch_security_group"
                    )
                    existing_sg_name = None if selected_sg == "<Select Security Group>" else selected_sg
                else:
                    existing_sg_name = None

                if sg_option == "Create new with default rules":
                    st.markdown("<div style='color:#94a3b8;font-size:0.88rem;margin:0.2rem 0 0.35rem;'>Default security group will include:</div>", unsafe_allow_html=True)
                    ports_default = st.multiselect(
                        "Open ports (for new security group)",
                        ["SSH (22)", "HTTP (80)", "HTTPS (443)", "Custom (3000)"],
                        default=["SSH (22)", "HTTP (80)"],
                        key="open_ports"
                    )
                else:
                    ports_default = []

                st.markdown("<div class='nav-group-label'>06 — Advanced</div>", unsafe_allow_html=True)
                user_data = st.text_area(
                    "Enter user data script (bash/shell)",
                    placeholder="#!/bin/bash\necho 'Hello World'",
                    height=120,
                    key="launch_user_data"
                )

                launch_submitted = st.form_submit_button("Launch EC2 Instance", use_container_width=True)

            if launch_submitted:
                if not ami_id:
                    st.warning("Please select an AMI.")
                else:
                    try:
                        run_params = {
                            "ImageId": ami_id,
                            "InstanceType": instance_type,
                            "MinCount": 1,
                            "MaxCount": 1
                        }

                        if key_name:
                            run_params["KeyName"] = key_name

                        sg_needs_creation = sg_option == "Create new with default rules"
                        security_group_id = None
                        if sg_needs_creation:
                            sg_name = f"ec2-launch-{int(time.time() * 1000)}"
                            vpc_id = None
                            if selected_vpc and selected_vpc != "<Default VPC>":
                                vpc_id = selected_vpc.split("(")[-1].rstrip(")")

                            create_sg_params = {
                                "GroupName": sg_name,
                                "Description": "Security group for EC2 launch from S3 Manager"
                            }
                            if vpc_id:
                                create_sg_params["VpcId"] = vpc_id

                            sg_response = ec2_client.create_security_group(**create_sg_params)
                            security_group_id = sg_response["GroupId"]

                            port_map = {
                                "SSH (22)": 22,
                                "HTTP (80)": 80,
                                "HTTPS (443)": 443,
                                "Custom (3000)": 3000
                            }

                            ip_permissions = []
                            for port_label in ports_default:
                                if port_label in port_map:
                                    ip_permissions.append({
                                        "IpProtocol": "tcp",
                                        "FromPort": port_map[port_label],
                                        "ToPort": port_map[port_label],
                                        "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                                    })

                            if ip_permissions:
                                ec2_client.authorize_security_group_ingress(
                                    GroupId=security_group_id,
                                    IpPermissions=ip_permissions
                                )

                            run_params["SecurityGroupIds"] = [security_group_id]
                        elif existing_sg_name:
                            sg_details = ec2_client.describe_security_groups(GroupNames=[existing_sg_name])
                            sg_ids = [sg["GroupId"] for sg in sg_details.get("SecurityGroups", [])]
                            if sg_ids:
                                run_params["SecurityGroupIds"] = sg_ids

                        if selected_subnet != "<Default Subnet>":
                            subnet_id = selected_subnet.split("(")[-1].rstrip(")")
                            run_params["NetworkInterfaces"] = [{
                                "SubnetId": subnet_id,
                                "DeviceIndex": 0,
                                "AssociatePublicIpAddress": True
                            }]

                        if user_data:
                            run_params["UserData"] = user_data

                        if instance_name:
                            run_params["TagSpecifications"] = [{
                                "ResourceType": "instance",
                                "Tags": [{"Key": "Name", "Value": instance_name}]
                            }]

                        with st.spinner("Launching EC2 instance..."):
                            run_response = ec2_client.run_instances(**run_params)

                        instance_id = run_response["Instances"][0]["InstanceId"]
                        st.success(f"Instance launch initiated: {instance_id}")
                        append_log(f"Launched EC2 instance {instance_id}")

                        with st.spinner(f"Waiting for instance {instance_id} to reach running state..."):
                            waiter = ec2_client.get_waiter("instance_running")
                            waiter.wait(InstanceIds=[instance_id])

                        instance_response = ec2_client.describe_instances(InstanceIds=[instance_id])
                        instance = instance_response["Reservations"][0]["Instances"][0]

                        st.subheader("Instance Details")
                        st.write(f"**Instance ID:** {instance.get('InstanceId', 'N/A')}")
                        st.write(f"**Public IPv4 Address:** {instance.get('PublicIpAddress', 'N/A')}")

                        state = instance.get("State", {})
                        st.write(f"**Instance State:** {state.get('Name', 'N/A')}")

                        if "KeyName" in instance:
                            st.write(f"**Key Pair:** {instance['KeyName']}")

                        append_log(f"EC2 instance {instance_id} is now running")

                    except ec2_client.exceptions.ClientError as e:
                        st.error(f"AWS API Error: {e.response['Error']['Message']}")
                    except Exception as e:
                        st.error(f"Failed to launch instance: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Monitoring":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Monitoring overview</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Quick health signals for your AWS resources.</div>", unsafe_allow_html=True)

        if not cloudwatch_client:
            st.info("Connect to AWS first to enable CloudWatch monitoring.")
        else:
            try:
                metric_list = cloudwatch_client.list_metrics()
                metrics = metric_list.get("Metrics", [])
                ec2_metrics = [m for m in metrics if m.get("Namespace") == "AWS/EC2"]
                s3_metrics = [m for m in metrics if m.get("Namespace") == "AWS/S3"]
                red_metrics = [m for m in metrics if m.get("Namespace") in ["AWS/EC2", "AWS/S3"] and any(d.get("Name") == "InstanceId" for d in m.get("Dimensions", []))]

                c1, c2, c3 = st.columns(3)
                c1.metric("EC2 metrics", len(ec2_metrics))
                c2.metric("S3 metrics", len(s3_metrics))
                c3.metric("Tracked dimensions", len(red_metrics))

                st.subheader("CloudWatch metric samples")
                if ec2_metrics:
                    st.write("EC2 sample metrics:")
                    for metric in ec2_metrics[:5]:
                        st.write(f"• {metric.get('MetricName')} | Dimensions: {metric.get('Dimensions', [])}")
                else:
                    st.info("No EC2 CloudWatch metrics were returned for this account and region.")

                if s3_metrics:
                    st.write("S3 sample metrics:")
                    for metric in s3_metrics[:5]:
                        st.write(f"• {metric.get('MetricName')} | Dimensions: {metric.get('Dimensions', [])}")
            except Exception as e:
                st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "CloudWatch Alerts":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>CloudWatch alarms</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Create and review basic health-based alarms.</div>", unsafe_allow_html=True)

        if not cloudwatch_client:
            st.info("Connect to AWS first to enable CloudWatch alarm management.")
        else:
            try:
                alarm_response = cloudwatch_client.describe_alarms()
                alarms = alarm_response.get("MetricAlarms", [])
                if alarms:
                    for alarm in alarms:
                        alarm_name = alarm.get("AlarmName", "unknown")
                        alarm_state = alarm.get("StateValue", "UNKNOWN")
                        alarm_metric = alarm.get("MetricName", "N/A")
                        col1, col2, col3 = st.columns([2, 1, 1])
                        col1.write(f"{alarm_name} — {alarm_metric}")
                        col2.write(alarm_state)
                        if col3.button("Delete", key=f"delete_alarm_{alarm_name}"):
                            st.warning(f"This will delete the alarm '{alarm_name}'.")
                            confirm = st.button(f"Confirm delete {alarm_name}", key=f"confirm_delete_{alarm_name}")
                            if confirm:
                                cloudwatch_client.delete_alarms(AlarmNames=[alarm_name])
                                append_log(f"Deleted CloudWatch alarm {alarm_name}")
                                st.success(f"Alarm {alarm_name} deleted.")
                                st.rerun()
                else:
                    st.info("No CloudWatch alarms were found.")

                sns_topics = []
                if sns_client:
                    try:
                        sns_topics = sns_client.list_topics().get("Topics", [])
                    except Exception:
                        sns_topics = []
                topic_arns = [topic["TopicArn"] for topic in sns_topics]

                st.subheader("SNS topics")
                if topic_arns:
                    for topic_arn in topic_arns:
                        try:
                            subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn).get("Subscriptions", [])
                            st.write(f"• {topic_arn} | Subscriptions: {len(subscriptions)}")
                        except Exception as e:
                            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "Unknown")
                            st.warning(f"• {topic_arn} | Subscriptions: UNABLE TO VERIFY ({error_code})")
                else:
                    st.info("No SNS topics discovered.")

                with st.form("create_sns_topic_form"):
                    sns_topic_name = st.text_input("SNS topic name", placeholder="cloudops-alerts")
                    create_topic = st.form_submit_button("Create SNS topic", use_container_width=True)
                if create_topic and sns_topic_name:
                    try:
                        topic_response = sns_client.create_topic(Name=sns_topic_name)
                        arn = topic_response["TopicArn"]
                        append_log(f"SNS_TOPIC_CREATED:{sns_topic_name}")
                        st.success(f"SNS topic {sns_topic_name} created: {arn}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Unable to create SNS topic: {e}")

                if topic_arns:
                    selected_sns_topic_arn = st.selectbox("SNS topic for email subscription", ["<Select topic>"] + topic_arns, key="sns_topic_for_email")
                    if selected_sns_topic_arn != "<Select topic>":
                        email_address = st.text_input("Email address", placeholder="user@example.com", key="sns_email_address")
                        if st.button("Create SNS email subscription"):
                            if not email_address:
                                st.warning("Provide an email address first.")
                            else:
                                try:
                                    sns_client.subscribe(TopicArn=selected_sns_topic_arn, Protocol="email", Endpoint=email_address)
                                    append_log(f"SNS_SUBSCRIPTION_CREATED:{selected_sns_topic_arn}:{email_address}")
                                    st.success(f"Subscription created for {email_address} on {selected_sns_topic_arn}")
                                except Exception as e:
                                    st.error(f"Unable to create email subscription: {e}")

                with st.form("create_alarm_form"):
                    alarm_name = st.text_input("Alarm name", "cloudops-ec2-cpu")
                    metrics = ["CPUUtilization", "StatusCheckFailed_Instance", "BucketSizeBytes", "NumberOfObjects"]
                    metric_name = st.selectbox("Metric name", metrics)
                    namespace = st.selectbox("Namespace", ["AWS/EC2", "AWS/S3"])
                    threshold = st.number_input("Threshold", min_value=0.0, value=80.0, step=1.0)
                    selected_alarm_sns = st.selectbox("SNS topic for alarm action", ["<No topic>"] + topic_arns, key="alarm_sns_topic")
                    create_alarm = st.form_submit_button("Create alarm", use_container_width=True)

                if create_alarm:
                    try:
                        alarm_args = {
                            "AlarmName": alarm_name,
                            "ComparisonOperator": "GreaterThanThreshold",
                            "EvaluationPeriods": 1,
                            "MetricName": metric_name,
                            "Namespace": namespace,
                            "Period": 300,
                            "Statistic": "Average",
                            "Threshold": threshold,
                            "TreatMissingData": "notBreaching",
                        }
                        if selected_alarm_sns != "<No topic>":
                            alarm_args["AlarmActions"] = [selected_alarm_sns]
                        cloudwatch_client.put_metric_alarm(**alarm_args)
                        append_log(f"CLOUDWATCH_ALARM_WITH_SNS_CREATED:{alarm_name}")
                        st.success(f"Alarm {alarm_name} created.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            except Exception as e:
                st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Lambda":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Lambda overview</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Review Lambda functions and invoke them with explicit confirmation.</div>", unsafe_allow_html=True)

        if not lambda_client:
            st.info("Connect to AWS first to enable Lambda monitoring.")
        else:
            try:
                functions = lambda_client.list_functions().get("Functions", [])
                if not functions:
                    st.info("No Lambda functions were returned for this account.")
                else:
                    function_names = [fn["FunctionName"] for fn in functions]
                    selected_function = st.selectbox("Select Lambda function", function_names)
                    if st.button("Invoke selected function", use_container_width=True):
                        st.warning("This will invoke the selected Lambda function in AWS.")
                        confirm = st.button("Confirm invocation", key="confirm_lambda_invoke")
                        if confirm:
                            response = lambda_client.invoke(
                                FunctionName=selected_function,
                                InvocationType="RequestResponse",
                                Payload=json.dumps({"source": "cloudops-console"}).encode("utf-8"),
                            )
                            payload = response.get("Payload")
                            output = payload.read().decode("utf-8", errors="ignore") if payload else "{}"
                            st.success(f"Lambda invocation completed for {selected_function}.")
                            st.code(output[:2000], language="json")
                            append_log(f"Invoked Lambda function {selected_function}")
                            st.rerun()

                    st.write("Function inventory:")
                    for function in functions[:10]:
                        st.write(f"• {function.get('FunctionName')} — Runtime: {function.get('Runtime', 'N/A')}")
            except Exception as e:
                st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Network":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Network inventory</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Inspect the VPC, subnet, route table, gateway, and NACL resources in the connected region.</div>", unsafe_allow_html=True)

        if not ec2_client:
            st.info("Connect to AWS first to enable network inventory.")
        else:
            try:
                vpcs = ec2_client.describe_vpcs().get("Vpcs", [])
                subnets = ec2_client.describe_subnets().get("Subnets", [])
                route_tables = ec2_client.describe_route_tables().get("RouteTables", [])
                internet_gateways = ec2_client.describe_internet_gateways().get("InternetGateways", [])
                nat_gateways = ec2_client.describe_nat_gateways().get("NatGateways", []) if hasattr(ec2_client, "describe_nat_gateways") else []
                network_acls = ec2_client.describe_network_acls().get("NetworkAcls", [])

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("VPCs", len(vpcs))
                c2.metric("Subnets", len(subnets))
                c3.metric("Route tables", len(route_tables))
                c4.metric("NACLs", len(network_acls))

                if vpcs:
                    st.write("VPCs:")
                    for vpc in vpcs[:10]:
                        st.write(f"• {vpc.get('VpcId')} — {safe_tag_value(vpc.get('Tags'), 'Name')}")
                if subnets:
                    st.write("Subnets:")
                    for subnet in subnets[:10]:
                        st.write(f"• {subnet.get('SubnetId')} — {subnet.get('AvailabilityZone')} — {safe_tag_value(subnet.get('Tags'), 'Name')}")
                if nat_gateways:
                    st.write("NAT gateways:")
                    for nat_gateway in nat_gateways[:5]:
                        st.write(f"• {nat_gateway.get('NatGatewayId')} — {nat_gateway.get('State')}")
                if network_acls:
                    st.write("Network ACLs:")
                    for nacl in network_acls[:10]:
                        st.write(f"• {nacl.get('NetworkAclId')} — VPC {nacl.get('VpcId')} — Subnets {nacl.get('Associations', [])[:3]}")
            except Exception as e:
                st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Security":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Security review</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Review IAM identities, EC2 security groups, EBS encryption, and hardening posture.</div>", unsafe_allow_html=True)

        if not (iam_client and ec2_client):
            st.info("Connect to AWS first to enable security inventory.")
        else:
            try:
                users = iam_client.list_users().get("Users", [])
                roles = iam_client.list_roles().get("Roles", [])
                policies = iam_client.list_policies(Scope="Local").get("Policies", [])
                security_groups = ec2_client.describe_security_groups().get("SecurityGroups", [])
                volumes = ec2_client.describe_volumes().get("Volumes", [])

                c1, c2, c3 = st.columns(3)
                c1.metric("IAM users", len(users))
                c2.metric("IAM roles", len(roles))
                c3.metric("Security groups", len(security_groups))

                if users:
                    st.write("IAM users:")
                    for user in users[:10]:
                        st.write(f"• {user.get('UserName')} — {user.get('Arn')}")
                if security_groups:
                    st.write("Security groups:")
                    for sg in security_groups[:10]:
                        st.write(f"• {sg.get('GroupName')} — {sg.get('GroupId')}")
                        open_critical = False
                        open_warning = False
                        for permission in sg.get("IpPermissions", []):
                            for ip_range in permission.get("IpRanges", []):
                                if ip_range.get("CidrIp") == "0.0.0.0/0":
                                    if permission.get("FromPort") in [22, 3389] or permission.get("IpProtocol") == "-1":
                                        open_critical = True
                                    elif permission.get("FromPort") in [80, 443] or permission.get("FromPort") is None:
                                        open_warning = True
                        if open_critical:
                            st.warning(f"CRITICAL: SSH or wide access is open on security group {sg.get('GroupName')}.")
                        elif open_warning:
                            st.warning(f"WARNING: Application access is exposed to 0.0.0.0/0 on security group {sg.get('GroupName')}.")
                        else:
                            st.success(f"Verified: {sg.get('GroupName')} is not publicly exposed by default.")
                if volumes:
                    st.subheader("EBS encryption")
                    for volume in volumes[:10]:
                        st.write(f"• {volume.get('VolumeId')} — Instance: {volume.get('Attachments', [{}])[0].get('InstanceId', 'N/A')} — Size: {volume.get('Size')} GiB — Encrypted: {volume.get('Encrypted')} — State: {volume.get('State')}")
                if policies:
                    st.write("Local policies:")
                    for policy in policies[:10]:
                        st.write(f"• {policy.get('PolicyName')} — {policy.get('Arn')}")
            except Exception as e:
                st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Audit":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Audit trail</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Review the local session log and optional DynamoDB audit table.</div>", unsafe_allow_html=True)

        events = load_audit_events()
        if not events:
            st.info("No audit events recorded yet.")
        else:
            for event in reversed(events[-20:]):
                st.write(f"• {event.get('timestamp', 'unknown')} — {event.get('message', 'No message')}")

        if dynamodb_client:
            try:
                tables = dynamodb_client.list_tables().get("TableNames", [])
                if tables:
                    st.write("DynamoDB tables detected:")
                    st.write(tables)
            except Exception as e:
                st.warning(f"DynamoDB audit table is unavailable: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Security & Compliance":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Security & compliance</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Review encryption, public exposure, IAM posture, and CloudTrail visibility.</div>", unsafe_allow_html=True)

        if not (client and ec2_client and iam_client):
            st.info("Connect to AWS first to enable security checks.")
        else:
            try:
                bucket_results = []
                for bucket_name in bucket_names:
                    status = {"bucket": bucket_name, "encryption": "UNABLE TO VERIFY", "versioning": "UNABLE TO VERIFY", "public_access_block": "UNABLE TO VERIFY", "bucket_policy": "UNABLE TO VERIFY"}
                    try:
                        client.get_bucket_encryption(Bucket=bucket_name)
                        status["encryption"] = "Verified"
                    except Exception:
                        pass
                    try:
                        versioning = client.get_bucket_versioning(Bucket=bucket_name).get("Status")
                        status["versioning"] = "Verified" if versioning in ["Enabled", "Suspended"] else "WARNING"
                    except Exception:
                        pass
                    try:
                        block = client.get_public_access_block(Bucket=bucket_name)
                        status["public_access_block"] = "Verified" if block.get("PublicAccessBlockConfiguration", {}).get("BlockPublicAcls") else "WARNING"
                    except Exception:
                        pass
                    try:
                        client.get_bucket_policy(Bucket=bucket_name)
                        status["bucket_policy"] = "WARNING"
                    except Exception:
                        pass
                    bucket_results.append(status)

                if bucket_results:
                    st.subheader("S3 security checks")
                    for item in bucket_results:
                        st.write(f"• {item['bucket']} — Encryption: {item['encryption']} | Versioning: {item['versioning']} | Public access: {item['public_access_block']} | Policy: {item['bucket_policy']}")

                sg_results = ec2_client.describe_security_groups().get("SecurityGroups", [])
                st.subheader("Security group review")
                for sg in sg_results[:10]:
                    rules = []
                    open_critical = False
                    for permission in sg.get("IpPermissions", []):
                        for ip_range in permission.get("IpRanges", []):
                            cidr = ip_range.get("CidrIp")
                            if cidr == "0.0.0.0/0":
                                if permission.get("FromPort") in [22, 3389] or permission.get("IpProtocol") == "-1":
                                    open_critical = True
                                elif permission.get("FromPort") in [80, 443] or permission.get("FromPort") is None:
                                    open_critical = True
                            rules.append(f"{permission.get('IpProtocol')} {permission.get('FromPort')}-{permission.get('ToPort')} from {cidr}")
                    st.write(f"• {sg.get('GroupName')} — {', '.join(rules) if rules else 'No open ingress rules'}")
                    if open_critical:
                        st.warning(f"CRITICAL: Security group {sg.get('GroupName')} exposes SSH or application traffic to 0.0.0.0/0.")
                    else:
                        st.success(f"Verified: {sg.get('GroupName')} is not exposing public ingress beyond the recommended pattern.")

                iam_roles = iam_client.list_roles().get("Roles", [])
                st.subheader("IAM least privilege review")
                for role in iam_roles[:10]:
                    policy_arns = [p["Arn"] for p in iam_client.list_attached_role_policies(RoleName=role["RoleName"]).get("AttachedPolicies", [])]
                    if any("AdministratorAccess" in arn for arn in policy_arns):
                        st.warning(f"Role {role['RoleName']} has a broad AdministratorAccess policy attached.")
                    else:
                        st.write(f"• {role['RoleName']} — attached policies: {len(policy_arns)}")

                if cloudtrail_client:
                    trails = cloudtrail_client.describe_trails().get("trailList", [])
                    if trails:
                        st.subheader("CloudTrail")
                        for trail in trails[:5]:
                            st.write(f"• {trail.get('Name')} — IsMultiRegionTrail: {trail.get('IsMultiRegionTrail')} — LogFileValidationEnabled: {trail.get('LogFileValidationEnabled')}")
                    else:
                        st.info("CloudTrail trails were not discoverable in this account.")

                st.markdown("<div class='login-note'>Security Recommendations: restrict SSH to a trusted CIDR, avoid public app ingress, enable S3 encryption/versioning, and attach least-privilege IAM policies.</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "High Availability & Scaling":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>High Availability & Scaling</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Review ALBs, target groups, ASGs, and launch templates for a resilient multi-AZ AWS architecture.</div>", unsafe_allow_html=True)

        if not (elbv2_client and autoscaling_client and ec2_client):
            st.info("Connect to AWS first to enable ALB and Auto Scaling discovery.")
        else:
            try:
                lbs = elbv2_client.describe_load_balancers().get("LoadBalancers", [])
                target_groups = elbv2_client.describe_target_groups().get("TargetGroups", [])
                asgs = autoscaling_client.describe_auto_scaling_groups().get("AutoScalingGroups", [])
                launch_templates = ec2_client.describe_launch_templates().get("LaunchTemplates", [])
                running_instances = []
                try:
                    reservations = ec2_client.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running"]}]).get("Reservations", [])
                    for reservation in reservations:
                        for instance in reservation.get("Instances", []):
                            running_instances.append(instance)
                except Exception:
                    running_instances = []

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ALBs", len(lbs))
                c2.metric("Target groups", len(target_groups))
                c3.metric("ASGs", len(asgs))
                c4.metric("Launch templates", len(launch_templates))

                if lbs:
                    st.subheader("Application Load Balancers")
                    for lb in lbs:
                        subnet_azs = [az.get("ZoneName") for az in lb.get("AvailabilityZones", [])]
                        multi_az = "Verified" if len(subnet_azs) >= 2 else "WARNING"
                        st.write(f"• {lb.get('LoadBalancerName')} — {lb.get('Scheme')} | {lb.get('State', {}).get('Code')} | AZs: {len(subnet_azs)} | Multi-AZ: {multi_az} | DNS: {lb.get('DNSName')}")
                        listeners = elbv2_client.describe_listeners(LoadBalancerArn=lb.get("LoadBalancerArn")).get("Listeners", [])
                        for listener in listeners:
                            proto = listener.get("Protocol")
                            port = listener.get("Port")
                            cert = listener.get("Certificates")
                            tls_status = "Verified" if proto == "HTTPS" and cert else "WARNING"
                            st.write(f"   - Listener: {proto}:{port} | TLS: {tls_status} | Certs: {len(cert) if cert else 0}")

                if target_groups:
                    st.subheader("Target groups")
                    for tg in target_groups:
                        targets = elbv2_client.describe_target_health(TargetGroupArn=tg["TargetGroupArn"]).get("TargetHealthDescriptions", [])
                        st.write(f"• {tg.get('TargetGroupName')} — {tg.get('Protocol')}:{tg.get('Port')} | {tg.get('TargetType')} | Registered targets: {len(targets)}")
                        for target in targets[:5]:
                            health = target.get("TargetHealth", {})
                            st.write(f"   - Target ID: {target.get('Target', {}).get('Id')} | Port: {target.get('Target', {}).get('Port')} | State: {health.get('State')} | Reason: {health.get('Reason', 'N/A')} | Description: {health.get('Description', 'N/A')}")

                    st.subheader("Register targets")
                    target_group_options = [tg["TargetGroupArn"] for tg in target_groups]
                    selected_tg_arn = st.selectbox("Target group", ["<Select target group>"] + target_group_options, key="target_group_register")
                    target_instance_ids = [inst["InstanceId"] for inst in running_instances]
                    selected_targets = st.multiselect("EC2 instances", target_instance_ids, key="target_group_instances")
                    target_port = st.number_input("Target port", min_value=1, max_value=65535, value=80, key="target_group_port")
                    reg_col, dereg_col = st.columns(2)
                    if reg_col.button("Register Targets") and selected_tg_arn != "<Select target group>" and selected_targets:
                        try:
                            elbv2_client.register_targets(TargetGroupArn=selected_tg_arn, Targets=[{"Id": instance_id, "Port": target_port} for instance_id in selected_targets])
                            append_log(f"TARGET_REGISTERED:{selected_tg_arn}:{','.join(selected_targets)}")
                            st.success(f"Registered {len(selected_targets)} target(s) to {selected_tg_arn}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Unable to register targets: {e}")
                    if dereg_col.button("Deregister Targets") and selected_tg_arn != "<Select target group>" and selected_targets:
                        try:
                            elbv2_client.deregister_targets(TargetGroupArn=selected_tg_arn, Targets=[{"Id": instance_id, "Port": target_port} for instance_id in selected_targets])
                            append_log(f"TARGET_DEREGISTERED:{selected_tg_arn}:{','.join(selected_targets)}")
                            st.success(f"Deregistered {len(selected_targets)} target(s) from {selected_tg_arn}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Unable to deregister targets: {e}")

                if asgs:
                    st.subheader("Auto Scaling Groups")
                    for asg in asgs:
                        st.write(f"• {asg.get('AutoScalingGroupName')} — Min:{asg.get('MinSize')} Desired:{asg.get('DesiredCapacity')} Max:{asg.get('MaxSize')} | AZs:{len(asg.get('AvailabilityZones', []))} | Health:{asg.get('HealthCheckType')}")

                st.subheader("ASG scaling policy")
                asg_policy_names = [asg["AutoScalingGroupName"] for asg in asgs] if asgs else []
                if asg_policy_names:
                    selected_asg_for_policy = st.selectbox("ASG", asg_policy_names, key="asg_for_policy")
                    existing_policies = autoscaling_client.describe_policies(AutoScalingGroupName=selected_asg_for_policy).get("ScalingPolicies", [])
                    if existing_policies:
                        st.write("Existing scaling policies:")
                        for policy in existing_policies:
                            st.write(f"• {policy.get('PolicyName')} — metric {policy.get('PolicyType')} — target {policy.get('TargetTrackingConfiguration', {}).get('TargetValue')}" )
                    else:
                        st.info("No scaling policies found for the selected ASG.")
                else:
                    st.info("No Auto Scaling Groups found to attach a target tracking policy.")

                with st.form("create_scaling_policy_form"):
                    asg_policy_name = st.text_input("ASG", value=(asg_policy_names[0] if asg_policy_names else ""), key="asg_policy_name_text")
                    policy_name = st.text_input("Policy name", placeholder="cloudops-cpu-policy")
                    target_cpu = st.number_input("Target CPU %", min_value=10.0, max_value=100.0, value=70.0, step=1.0)
                    create_policy = st.form_submit_button("Create target tracking policy", use_container_width=True)

                if create_policy and asg_policy_name and policy_name:
                    try:
                        autoscaling_client.put_scaling_policy(
                            AutoScalingGroupName=asg_policy_name,
                            PolicyName=policy_name,
                            PolicyType="TargetTrackingScaling",
                            TargetTrackingConfiguration={
                                "PredefinedMetricSpecification": {
                                    "PredefinedMetricType": "ASGAverageCPUUtilization"
                                },
                                "TargetValue": float(target_cpu),
                            },
                        )
                        append_log(f"SCALING_POLICY_CREATED:{policy_name}:{asg_policy_name}:{target_cpu}")
                        st.success(f"Target tracking policy {policy_name} created for {asg_policy_name}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Unable to create scaling policy: {e}")

                st.subheader("Create ALB")
                with st.form("create_alb_form"):
                    alb_name = st.text_input("Load balancer name", placeholder="cloudops-alb")
                    scheme = st.selectbox("Scheme", ["internet-facing", "internal"])
                    vpc_options = [v["VpcId"] for v in ec2_client.describe_vpcs().get("Vpcs", [])]
                    selected_vpc = st.selectbox("VPC", vpc_options) if vpc_options else st.text_input("VPC", "")
                    subnet_options = [s["SubnetId"] for s in ec2_client.describe_subnets().get("Subnets", [])]
                    subnet_ids = st.multiselect("Public subnets", subnet_options)
                    sg_ids = [sg["GroupId"] for sg in ec2_client.describe_security_groups().get("SecurityGroups", [])]
                    security_group = st.selectbox("Security group", sg_ids) if sg_ids else st.text_input("Security group", "")
                    listener_port = st.selectbox("Listener port", [80, 443])
                    listener_protocol = st.selectbox("Protocol", ["HTTP", "HTTPS"])
                    create_alb = st.form_submit_button("Create ALB", use_container_width=True)

                if create_alb and alb_name:
                    try:
                        az_names = {subnet["SubnetId"]: subnet.get("AvailabilityZone") for subnet in ec2_client.describe_subnets(SubnetIds=subnet_ids).get("Subnets", [])} if subnet_ids else {}
                        distinct_azs = set(az_names.values())
                        if scheme == "internet-facing" and (len(subnet_ids) < 2 or len(distinct_azs) < 2):
                            st.error("Internet-facing ALB creation requires at least 2 subnets in different Availability Zones.")
                        else:
                            response = elbv2_client.create_load_balancer(
                                Name=alb_name,
                                Subnets=subnet_ids,
                                SecurityGroups=[security_group] if security_group else [],
                                Scheme=scheme,
                                Type="application",
                                IpAddressType="ipv4",
                            )
                            lb_arn = response["LoadBalancers"][0]["LoadBalancerArn"]
                            elbv2_client.create_listener(
                                LoadBalancerArn=lb_arn,
                                Protocol=listener_protocol,
                                Port=listener_port,
                                DefaultActions=[{"Type": "fixed-response", "FixedResponseConfig": {"ContentType": "text/plain", "MessageBody": "CloudOps Console", "StatusCode": "200"}, "Order": 1}],
                            )
                            append_log(f"ALB_CREATED:{alb_name}")
                            st.success(f"ALB {alb_name} created.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Unable to create ALB: {e}")

                st.subheader("Create target group")
                with st.form("create_target_group_form"):
                    target_group_name = st.text_input("Target group name", placeholder="cloudops-tg")
                    protocol = st.selectbox("Protocol", ["HTTP", "HTTPS"])
                    port = st.selectbox("Port", [80, 443, 8080])
                    target_type = st.selectbox("Target type", ["instance", "ip"])
                    tg_vpc = st.selectbox("Target group VPC", vpc_options) if vpc_options else st.text_input("Target group VPC", "")
                    create_tg = st.form_submit_button("Create target group", use_container_width=True)

                if create_tg and target_group_name:
                    try:
                        tg_response = elbv2_client.create_target_group(
                            Name=target_group_name,
                            Protocol=protocol,
                            Port=port,
                            VpcId=tg_vpc,
                            TargetType=target_type,
                            HealthCheckProtocol=protocol,
                            HealthCheckPort=str(port),
                            HealthCheckPath="/",
                        )
                        append_log(f"TARGET_GROUP_CREATED:{target_group_name}")
                        st.success(f"Target group {target_group_name} created: {tg_response['TargetGroups'][0]['TargetGroupArn']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Unable to create target group: {e}")

                st.subheader("Create Auto Scaling Group")
                launch_templates = ec2_client.describe_launch_templates().get("LaunchTemplates", [])
                template_options = [lt["LaunchTemplateName"] for lt in launch_templates]
                with st.form("create_asg_form"):
                    asg_name = st.text_input("ASG name", placeholder="cloudops-asg")
                    min_size = st.number_input("Minimum", min_value=1, max_value=10, value=2)
                    desired_size = st.number_input("Desired", min_value=1, max_value=10, value=2)
                    max_size = st.number_input("Maximum", min_value=1, max_value=20, value=4)
                    asg_vpc = st.selectbox("ASG VPC", vpc_options) if vpc_options else st.text_input("ASG VPC", "")
                    asg_subnets = st.multiselect("ASG subnets", [s["SubnetId"] for s in ec2_client.describe_subnets().get("Subnets", [])])
                    asg_target_group = st.selectbox("Target group", [tg["TargetGroupArn"] for tg in target_groups]) if target_groups else st.text_input("Target group ARN", "")
                    asg_template = st.selectbox("Launch template", template_options) if template_options else st.text_input("Launch template name", "")
                    create_asg = st.form_submit_button("Create ASG", use_container_width=True)

                if create_asg and asg_name:
                    try:
                        subnet_azs = []
                        if asg_subnets:
                            subnet_azs = [subnet["AvailabilityZone"] for subnet in ec2_client.describe_subnets(SubnetIds=asg_subnets).get("Subnets", [])]
                        if min_size < 2 or desired_size < 2 or max_size < desired_size:
                            st.error("ASG validation: Minimum >= 2, Desired >= 2, Maximum >= Desired")
                        elif len(asg_subnets) < 2 or len(set(subnet_azs)) < 2:
                            st.warning("ASG is not configured for multi-AZ high availability. Add at least 2 subnets in different Availability Zones.")
                        else:
                            autoscaling_client.create_auto_scaling_group(
                                AutoScalingGroupName=asg_name,
                                LaunchTemplate={"LaunchTemplateId": next((lt["LaunchTemplateId"] for lt in launch_templates if lt["LaunchTemplateName"] == asg_template), None), "Version": "$Latest"} if asg_template else None,
                                MinSize=min_size,
                                DesiredCapacity=desired_size,
                                MaxSize=max_size,
                                VPCZoneIdentifier=",".join(asg_subnets),
                                TargetGroupARNs=[asg_target_group] if asg_target_group else [],
                                HealthCheckType="ELB",
                                HealthCheckGracePeriod=300,
                            )
                            append_log(f"ASG_CREATED:{asg_name}")
                            st.success(f"ASG {asg_name} created.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Unable to create ASG: {e}")

                st.subheader("Launch template")
                with st.form("create_launch_template_form"):
                    template_name = st.text_input("Template name", placeholder="cloudops-lt")
                    ami_id = st.text_input("AMI ID", placeholder="ami-xxxxxxxxxxxxxxxxx")
                    instance_type = st.selectbox("Instance type", ["t3.micro", "t3.small", "t3.medium"])
                    key_name = st.selectbox("Key pair", [kp["KeyName"] for kp in ec2_client.describe_key_pairs().get("KeyPairs", [])]) if ec2_client.describe_key_pairs().get("KeyPairs") else st.text_input("Key pair", "")
                    sg_id = st.selectbox("Security group", [sg["GroupId"] for sg in ec2_client.describe_security_groups().get("SecurityGroups", [])]) if ec2_client.describe_security_groups().get("SecurityGroups") else st.text_input("Security group", "")
                    user_script = st.text_area("User data", value="#!/bin/bash\nyum update -y\nyum install -y httpd\nsystemctl start httpd\nsystemctl enable httpd\nINSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)\nHOSTNAME=$(hostname)\necho \"<h1>Welcome from $INSTANCE_ID</h1><p>$HOSTNAME</p>\" > /var/www/html/index.html\n")
                    create_template = st.form_submit_button("Create launch template", use_container_width=True)

                if create_template and template_name:
                    try:
                        user_data_b64 = __import__("base64").b64encode(user_script.encode("utf-8")).decode("utf-8")
                        ec2_client.create_launch_template(
                            LaunchTemplateName=template_name,
                            LaunchTemplateData={
                                "ImageId": ami_id,
                                "InstanceType": instance_type,
                                "KeyName": key_name,
                                "SecurityGroupIds": [sg_id] if sg_id else [],
                                "UserData": user_data_b64,
                            },
                        )
                        append_log(f"LAUNCH_TEMPLATE_CREATED:{template_name}")
                        st.success(f"Launch template {template_name} created.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Unable to create launch template: {e}")
            except Exception as e:
                st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Architecture Overview":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Architecture overview</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Conceptual CIA-3 reference architecture for the current AWS account.</div>", unsafe_allow_html=True)

        st.code(
            """                         INTERNET\n                            |\n                            v\n                    Application ALB\n                       /       \\\n                      /         \\\n                   AZ-1         AZ-2\n                    |             |\n             Private Subnet Private Subnet\n                    |             |\n                  EC2           EC2\n                    \\             /\n                     \\           /\n                       Auto Scaling\n                            |\n          +-----------------+----------------+\n          |                 |                |\n          v                 v                v\n         S3             DynamoDB          Lambda\n\n          EC2 / ALB\n             |\n             v\n         CloudWatch\n             |\n             v\n            SNS\n             |\n             v\n           Email\n""",
            language="text",
        )

        st.write("VPC elements:")
        st.write("• Public subnets route through Internet Gateway")
        st.write("• Private subnets route through NAT Gateway where present")
        st.write("• ALB is used for inflow and health checking")
        st.write("• ASG provides replacement and scaling across AZs")
        st.write("• CloudWatch + SNS provide monitoring and alerting")

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "CIA-3 Validation":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>CIA-3 Architecture Validation</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Checklist-based validation of the current AWS environment for scalability, availability, security, and cost.</div>", unsafe_allow_html=True)

        def add_validation(results, category, label, status, details):
            results.append((category, label, status, details))

        validations = []
        section_errors = []

        # Core discovery calls reused across all CIA-3 checks.
        lbs = None
        target_groups = None
        asgs = None
        launch_templates = None
        vpcs = None
        subnets = None
        route_tables = None
        igws = None
        nat_gateways = None
        network_acls = None
        security_groups = None
        volumes = None

        if elbv2_client:
            try:
                lbs = elbv2_client.describe_load_balancers().get("LoadBalancers", [])
            except Exception as e:
                section_errors.append(f"ALB discovery error: {e}")
            try:
                target_groups = elbv2_client.describe_target_groups().get("TargetGroups", [])
            except Exception as e:
                section_errors.append(f"Target group discovery error: {e}")

        if autoscaling_client:
            try:
                asgs = autoscaling_client.describe_auto_scaling_groups().get("AutoScalingGroups", [])
            except Exception as e:
                section_errors.append(f"ASG discovery error: {e}")

        if ec2_client:
            try:
                launch_templates = ec2_client.describe_launch_templates().get("LaunchTemplates", [])
            except Exception as e:
                section_errors.append(f"Launch template discovery error: {e}")
            try:
                vpcs = ec2_client.describe_vpcs().get("Vpcs", [])
            except Exception as e:
                section_errors.append(f"VPC discovery error: {e}")
            try:
                subnets = ec2_client.describe_subnets().get("Subnets", [])
            except Exception as e:
                section_errors.append(f"Subnet discovery error: {e}")
            try:
                route_tables = ec2_client.describe_route_tables().get("RouteTables", [])
            except Exception as e:
                section_errors.append(f"Route table discovery error: {e}")
            try:
                igws = ec2_client.describe_internet_gateways().get("InternetGateways", [])
            except Exception as e:
                section_errors.append(f"Internet gateway discovery error: {e}")
            try:
                if hasattr(ec2_client, "describe_nat_gateways"):
                    nat_gateways = ec2_client.describe_nat_gateways().get("NatGateways", [])
                else:
                    nat_gateways = []
            except Exception as e:
                section_errors.append(f"NAT gateway discovery error: {e}")
            try:
                network_acls = ec2_client.describe_network_acls().get("NetworkAcls", [])
            except Exception as e:
                section_errors.append(f"NACL discovery error: {e}")
            try:
                security_groups = ec2_client.describe_security_groups().get("SecurityGroups", [])
            except Exception as e:
                section_errors.append(f"Security group discovery error: {e}")
            try:
                volumes = ec2_client.describe_volumes().get("Volumes", [])
            except Exception as e:
                section_errors.append(f"EBS discovery error: {e}")

        # SCALABILITY
        if lbs is None:
            add_validation(validations, "SCALABILITY", "ALB", "UNABLE TO VERIFY", "Unable to query load balancers")
        elif lbs:
            add_validation(validations, "SCALABILITY", "ALB", "PASS", f"Detected {len(lbs)} ALB(s)")
        else:
            add_validation(validations, "SCALABILITY", "ALB", "WARNING", "No ALBs detected")

        if target_groups is None:
            add_validation(validations, "SCALABILITY", "Target Group", "UNABLE TO VERIFY", "Unable to query target groups")
        elif target_groups:
            add_validation(validations, "SCALABILITY", "Target Group", "PASS", f"Detected {len(target_groups)} target group(s)")
        else:
            add_validation(validations, "SCALABILITY", "Target Group", "WARNING", "No target groups detected")

        if asgs is None:
            add_validation(validations, "SCALABILITY", "ASG", "UNABLE TO VERIFY", "Unable to query Auto Scaling Groups")
        elif asgs:
            add_validation(validations, "SCALABILITY", "ASG", "PASS", f"Detected {len(asgs)} ASG(s)")
        else:
            add_validation(validations, "SCALABILITY", "ASG", "WARNING", "No Auto Scaling Groups detected")

        if launch_templates is None:
            add_validation(validations, "SCALABILITY", "Launch Template", "UNABLE TO VERIFY", "Unable to query launch templates")
        elif launch_templates:
            add_validation(validations, "SCALABILITY", "Launch Template", "PASS", f"Detected {len(launch_templates)} launch template(s)")
        else:
            add_validation(validations, "SCALABILITY", "Launch Template", "WARNING", "No launch templates detected")

        # ASG policy validation (target-tracking with ASGAverageCPUUtilization).
        asg_policy_summaries = []
        if not autoscaling_client:
            add_validation(validations, "SCALABILITY", "Target Tracking Policy", "UNABLE TO VERIFY", "Auto Scaling client unavailable")
        elif asgs is None:
            add_validation(validations, "SCALABILITY", "Target Tracking Policy", "UNABLE TO VERIFY", "Unable to query Auto Scaling Groups")
        elif not asgs:
            add_validation(validations, "SCALABILITY", "Target Tracking Policy", "WARNING", "No ASGs detected")
        else:
            missing_policy = False
            policy_query_failed = False
            for asg in asgs:
                asg_name = asg.get("AutoScalingGroupName", "unknown")
                try:
                    policies = autoscaling_client.describe_policies(AutoScalingGroupName=asg_name).get("ScalingPolicies", [])
                    cpu_target_tracking = [
                        p for p in policies
                        if p.get("PolicyType") == "TargetTrackingScaling"
                        and p.get("TargetTrackingConfiguration", {}).get("PredefinedMetricSpecification", {}).get("PredefinedMetricType") == "ASGAverageCPUUtilization"
                    ]
                    if not cpu_target_tracking:
                        missing_policy = True
                    policy_targets = [
                        str(p.get("TargetTrackingConfiguration", {}).get("TargetValue")) for p in cpu_target_tracking
                    ]
                    asg_policy_summaries.append(
                        f"{asg_name}: min={asg.get('MinSize')} desired={asg.get('DesiredCapacity')} max={asg.get('MaxSize')} policy_count={len(cpu_target_tracking)} target={', '.join(policy_targets) if policy_targets else 'N/A'}"
                    )
                except Exception as e:
                    policy_query_failed = True
                    asg_policy_summaries.append(f"{asg_name}: UNABLE TO VERIFY policy details ({e})")
            if policy_query_failed:
                add_validation(validations, "SCALABILITY", "Target Tracking Policy", "UNABLE TO VERIFY", "One or more ASG policy lookups failed")
            elif missing_policy:
                add_validation(validations, "SCALABILITY", "Target Tracking Policy", "WARNING", "At least one ASG is missing ASGAverageCPUUtilization target-tracking policy")
            else:
                add_validation(validations, "SCALABILITY", "Target Tracking Policy", "PASS", "All ASGs have ASGAverageCPUUtilization target-tracking policy")

        # HIGH AVAILABILITY
        if subnets is None:
            add_validation(validations, "HIGH AVAILABILITY", "Multiple AZs", "UNABLE TO VERIFY", "Unable to query subnets")
        else:
            az_count = len({subnet.get("AvailabilityZone") for subnet in subnets if subnet.get("AvailabilityZone")})
            status = "PASS" if az_count > 1 else "WARNING"
            add_validation(validations, "HIGH AVAILABILITY", "Multiple AZs", status, f"Detected {az_count} AZ(s)")

        if lbs is None:
            add_validation(validations, "HIGH AVAILABILITY", "ALB Multi-AZ", "UNABLE TO VERIFY", "Unable to query ALBs")
        else:
            alb_multi_az_count = len([lb for lb in lbs if len(lb.get("AvailabilityZones", [])) > 1])
            if not lbs:
                add_validation(validations, "HIGH AVAILABILITY", "ALB Multi-AZ", "WARNING", "No ALBs detected")
            elif alb_multi_az_count == len(lbs):
                add_validation(validations, "HIGH AVAILABILITY", "ALB Multi-AZ", "PASS", f"All {len(lbs)} ALB(s) span multiple AZs")
            else:
                add_validation(validations, "HIGH AVAILABILITY", "ALB Multi-AZ", "WARNING", f"{alb_multi_az_count}/{len(lbs)} ALB(s) span multiple AZs")

        if asgs is None:
            add_validation(validations, "HIGH AVAILABILITY", "ASG Multi-AZ", "UNABLE TO VERIFY", "Unable to query ASGs")
        elif not asgs:
            add_validation(validations, "HIGH AVAILABILITY", "ASG Multi-AZ", "WARNING", "No ASGs detected")
        else:
            asg_multi_az_count = len([asg for asg in asgs if len(set(asg.get("AvailabilityZones", []))) > 1])
            if asg_multi_az_count == len(asgs):
                add_validation(validations, "HIGH AVAILABILITY", "ASG Multi-AZ", "PASS", f"All {len(asgs)} ASG(s) span multiple AZs")
            else:
                add_validation(validations, "HIGH AVAILABILITY", "ASG Multi-AZ", "WARNING", f"{asg_multi_az_count}/{len(asgs)} ASG(s) span multiple AZs")

        target_health_rows = []
        if target_groups is None:
            add_validation(validations, "HIGH AVAILABILITY", "Target Health", "UNABLE TO VERIFY", "Unable to query target groups")
        elif not target_groups:
            add_validation(validations, "HIGH AVAILABILITY", "Target Health", "WARNING", "No target groups detected")
        else:
            health_api_failed = False
            total_healthy = 0
            total_unhealthy = 0
            total_registered = 0
            for tg in target_groups:
                tg_name = tg.get("TargetGroupName", "unknown")
                tg_arn = tg.get("TargetGroupArn")
                try:
                    descriptions = elbv2_client.describe_target_health(TargetGroupArn=tg_arn).get("TargetHealthDescriptions", [])
                    registered = len(descriptions)
                    healthy = len([d for d in descriptions if d.get("TargetHealth", {}).get("State") == "healthy"])
                    unhealthy = len([d for d in descriptions if d.get("TargetHealth", {}).get("State") in ["unhealthy", "draining", "unused", "unavailable", "initial"]])
                    total_registered += registered
                    total_healthy += healthy
                    total_unhealthy += unhealthy
                    target_health_rows.append(f"{tg_name}: registered={registered}, healthy={healthy}, unhealthy={unhealthy}")
                except Exception as e:
                    health_api_failed = True
                    target_health_rows.append(f"{tg_name}: UNABLE TO VERIFY ({e})")
            if health_api_failed:
                add_validation(validations, "HIGH AVAILABILITY", "Target Health", "UNABLE TO VERIFY", "One or more target health queries failed")
            elif total_healthy > 0 and total_unhealthy == 0:
                add_validation(validations, "HIGH AVAILABILITY", "Target Health", "PASS", f"registered={total_registered}, healthy={total_healthy}, unhealthy={total_unhealthy}")
            else:
                add_validation(validations, "HIGH AVAILABILITY", "Target Health", "WARNING", f"registered={total_registered}, healthy={total_healthy}, unhealthy={total_unhealthy}")

        # SECURITY
        if iam_client:
            try:
                iam_roles = iam_client.list_roles().get("Roles", [])
                if iam_roles:
                    add_validation(validations, "SECURITY", "IAM", "PASS", f"Detected {len(iam_roles)} role(s)")
                else:
                    add_validation(validations, "SECURITY", "IAM", "WARNING", "No IAM roles detected")
            except Exception as e:
                add_validation(validations, "SECURITY", "IAM", "UNABLE TO VERIFY", str(e))

            try:
                high_privilege_roles = []
                iam_roles = iam_client.list_roles().get("Roles", [])
                for role in iam_roles[:50]:
                    attached = iam_client.list_attached_role_policies(RoleName=role.get("RoleName")).get("AttachedPolicies", [])
                    if any("AdministratorAccess" in policy.get("PolicyArn", "") for policy in attached):
                        high_privilege_roles.append(role.get("RoleName"))
                if high_privilege_roles:
                    add_validation(validations, "SECURITY", "Least Privilege analysis", "WARNING", f"Broad access roles: {', '.join(high_privilege_roles[:10])}")
                else:
                    add_validation(validations, "SECURITY", "Least Privilege analysis", "PASS", "No AdministratorAccess attachment detected on sampled roles")
            except Exception as e:
                add_validation(validations, "SECURITY", "Least Privilege analysis", "UNABLE TO VERIFY", str(e))
        else:
            add_validation(validations, "SECURITY", "IAM", "UNABLE TO VERIFY", "IAM client unavailable")
            add_validation(validations, "SECURITY", "Least Privilege analysis", "UNABLE TO VERIFY", "IAM client unavailable")

        if security_groups is None:
            add_validation(validations, "SECURITY", "Security Groups", "UNABLE TO VERIFY", "Unable to query security groups")
        else:
            public_exposure = False
            for sg in security_groups:
                for permission in sg.get("IpPermissions", []):
                    for ip_range in permission.get("IpRanges", []):
                        if ip_range.get("CidrIp") == "0.0.0.0/0":
                            public_exposure = True
            if public_exposure:
                add_validation(validations, "SECURITY", "Security Groups", "WARNING", "Public ingress (0.0.0.0/0) detected")
            else:
                add_validation(validations, "SECURITY", "Security Groups", "PASS", "No public ingress detected in current security groups")

        # S3 encryption and versioning checks are evidence-based per bucket.
        if client and bucket_names:
            s3_encryption_states = []
            s3_versioning_states = []
            s3_public_block_states = []
            for bucket_name in bucket_names:
                try:
                    client.get_bucket_encryption(Bucket=bucket_name)
                    s3_encryption_states.append((bucket_name, "PASS", "Server-side encryption configured"))
                except Exception as e:
                    error_code = getattr(e, "response", {}).get("Error", {}).get("Code")
                    if error_code == "ServerSideEncryptionConfigurationNotFoundError":
                        s3_encryption_states.append((bucket_name, "WARNING", "Encryption not configured"))
                    else:
                        s3_encryption_states.append((bucket_name, "UNABLE TO VERIFY", str(e)))

                try:
                    version_status = client.get_bucket_versioning(Bucket=bucket_name).get("Status")
                    if version_status == "Enabled":
                        s3_versioning_states.append((bucket_name, "PASS", "Versioning Enabled"))
                    else:
                        s3_versioning_states.append((bucket_name, "WARNING", f"Versioning status: {version_status or 'Not Enabled'}"))
                except Exception as e:
                    s3_versioning_states.append((bucket_name, "UNABLE TO VERIFY", str(e)))

                try:
                    block_cfg = client.get_public_access_block(Bucket=bucket_name).get("PublicAccessBlockConfiguration", {})
                    if block_cfg.get("BlockPublicAcls") and block_cfg.get("BlockPublicPolicy"):
                        s3_public_block_states.append((bucket_name, "PASS", "Public Access Block enabled"))
                    else:
                        s3_public_block_states.append((bucket_name, "WARNING", "Public Access Block partially configured"))
                except Exception as e:
                    s3_public_block_states.append((bucket_name, "UNABLE TO VERIFY", str(e)))

            encryption_statuses = {state for _, state, _ in s3_encryption_states}
            if "UNABLE TO VERIFY" in encryption_statuses:
                enc_status = "UNABLE TO VERIFY"
            elif "WARNING" in encryption_statuses:
                enc_status = "WARNING"
            else:
                enc_status = "PASS"
            add_validation(validations, "SECURITY", "S3 encryption", enc_status, f"Buckets checked: {len(s3_encryption_states)}")

            versioning_statuses = {state for _, state, _ in s3_versioning_states}
            if "UNABLE TO VERIFY" in versioning_statuses:
                versioning_status = "UNABLE TO VERIFY"
            elif "WARNING" in versioning_statuses:
                versioning_status = "WARNING"
            else:
                versioning_status = "PASS"
            add_validation(validations, "RELIABILITY", "S3 versioning", versioning_status, f"Buckets checked: {len(s3_versioning_states)}")

            public_block_statuses = {state for _, state, _ in s3_public_block_states}
            if "UNABLE TO VERIFY" in public_block_statuses:
                block_status = "UNABLE TO VERIFY"
            elif "WARNING" in public_block_statuses:
                block_status = "WARNING"
            else:
                block_status = "PASS"
            add_validation(validations, "SECURITY", "S3 Public Access Block", block_status, f"Buckets checked: {len(s3_public_block_states)}")
        elif client and not bucket_names:
            add_validation(validations, "SECURITY", "S3 encryption", "WARNING", "No buckets discovered")
            add_validation(validations, "RELIABILITY", "S3 versioning", "WARNING", "No buckets discovered")
            add_validation(validations, "SECURITY", "S3 Public Access Block", "WARNING", "No buckets discovered")
        else:
            add_validation(validations, "SECURITY", "S3 encryption", "UNABLE TO VERIFY", "S3 client unavailable")
            add_validation(validations, "RELIABILITY", "S3 versioning", "UNABLE TO VERIFY", "S3 client unavailable")
            add_validation(validations, "SECURITY", "S3 Public Access Block", "UNABLE TO VERIFY", "S3 client unavailable")

        if volumes is None:
            add_validation(validations, "SECURITY", "EBS encryption", "UNABLE TO VERIFY", "Unable to query EBS volumes")
            add_validation(validations, "RELIABILITY", "EBS encryption", "UNABLE TO VERIFY", "Unable to query EBS volumes")
        elif not volumes:
            add_validation(validations, "SECURITY", "EBS encryption", "WARNING", "No EBS volumes discovered")
            add_validation(validations, "RELIABILITY", "EBS encryption", "WARNING", "No EBS volumes discovered")
        else:
            encrypted_count = len([volume for volume in volumes if volume.get("Encrypted")])
            unencrypted_count = len(volumes) - encrypted_count
            ebs_status = "PASS" if unencrypted_count == 0 else "WARNING"
            add_validation(validations, "SECURITY", "EBS encryption", ebs_status, f"encrypted={encrypted_count}, unencrypted={unencrypted_count}")
            add_validation(validations, "RELIABILITY", "EBS encryption", ebs_status, f"encrypted={encrypted_count}, unencrypted={unencrypted_count}")

        # HTTPS/TLS validation on ALB listeners.
        if lbs is None:
            add_validation(validations, "SECURITY", "HTTPS/TLS", "UNABLE TO VERIFY", "Unable to query ALBs")
        elif not lbs:
            add_validation(validations, "SECURITY", "HTTPS/TLS", "WARNING", "No ALBs detected")
        else:
            tls_api_failed = False
            tls_warnings = 0
            listener_lines = []
            for lb in lbs:
                lb_name = lb.get("LoadBalancerName", "unknown")
                try:
                    listeners = elbv2_client.describe_listeners(LoadBalancerArn=lb.get("LoadBalancerArn")).get("Listeners", [])
                    has_https = any(listener.get("Protocol") == "HTTPS" for listener in listeners)
                    has_cert = any(listener.get("Protocol") == "HTTPS" and listener.get("Certificates") for listener in listeners)
                    if has_https and has_cert:
                        listener_lines.append(f"{lb_name}: HTTPS listener with certificate configured")
                    else:
                        tls_warnings += 1
                        listener_lines.append(f"{lb_name}: WARNING - only HTTP or HTTPS certificate missing")
                except Exception as e:
                    tls_api_failed = True
                    listener_lines.append(f"{lb_name}: UNABLE TO VERIFY ({e})")
            if tls_api_failed:
                add_validation(validations, "SECURITY", "HTTPS/TLS", "UNABLE TO VERIFY", "One or more ALB listener queries failed")
            elif tls_warnings == 0:
                add_validation(validations, "SECURITY", "HTTPS/TLS", "PASS", "All ALBs include HTTPS listener with certificate")
            else:
                add_validation(validations, "SECURITY", "HTTPS/TLS", "WARNING", f"{tls_warnings} ALB(s) missing HTTPS or certificate")

        if cloudtrail_client:
            try:
                trails = cloudtrail_client.describe_trails().get("trailList", [])
                if trails:
                    add_validation(validations, "SECURITY", "CloudTrail", "PASS", f"Detected {len(trails)} trail(s)")
                else:
                    add_validation(validations, "SECURITY", "CloudTrail", "WARNING", "No trails detected")
            except Exception as e:
                add_validation(validations, "SECURITY", "CloudTrail", "UNABLE TO VERIFY", str(e))
        else:
            add_validation(validations, "SECURITY", "CloudTrail", "UNABLE TO VERIFY", "CloudTrail client unavailable")

        # NETWORKING
        if vpcs is None:
            add_validation(validations, "NETWORKING", "VPC", "UNABLE TO VERIFY", "Unable to query VPCs")
        elif vpcs:
            add_validation(validations, "NETWORKING", "VPC", "PASS", f"Detected {len(vpcs)} VPC(s)")
        else:
            add_validation(validations, "NETWORKING", "VPC", "WARNING", "No VPCs detected")

        if subnets is None:
            add_validation(validations, "NETWORKING", "Public/Private subnet information", "UNABLE TO VERIFY", "Unable to query subnets")
        elif not subnets:
            add_validation(validations, "NETWORKING", "Public/Private subnet information", "WARNING", "No subnets detected")
        else:
            public_count = len([subnet for subnet in subnets if subnet.get("MapPublicIpOnLaunch")])
            private_count = len(subnets) - public_count
            add_validation(validations, "NETWORKING", "Public/Private subnet information", "PASS", f"public={public_count}, private={private_count}")

        if route_tables is None:
            add_validation(validations, "NETWORKING", "Route Tables", "UNABLE TO VERIFY", "Unable to query route tables")
        elif route_tables:
            add_validation(validations, "NETWORKING", "Route Tables", "PASS", f"Detected {len(route_tables)} route table(s)")
        else:
            add_validation(validations, "NETWORKING", "Route Tables", "WARNING", "No route tables detected")

        if igws is None:
            add_validation(validations, "NETWORKING", "Internet Gateway", "UNABLE TO VERIFY", "Unable to query internet gateways")
        elif igws:
            add_validation(validations, "NETWORKING", "Internet Gateway", "PASS", f"Detected {len(igws)} internet gateway(s)")
        else:
            add_validation(validations, "NETWORKING", "Internet Gateway", "WARNING", "No internet gateways detected")

        if nat_gateways is None:
            add_validation(validations, "NETWORKING", "NAT Gateway", "UNABLE TO VERIFY", "Unable to query NAT gateways")
        else:
            active_nat = [nat for nat in nat_gateways if nat.get("State") != "deleted"]
            if active_nat:
                add_validation(validations, "NETWORKING", "NAT Gateway", "PASS", f"Detected {len(active_nat)} active NAT gateway(s)")
            else:
                add_validation(validations, "NETWORKING", "NAT Gateway", "WARNING", "No active NAT gateways detected")

        if network_acls is None:
            add_validation(validations, "NETWORKING", "Network ACLs", "UNABLE TO VERIFY", "Unable to query network ACLs")
        elif network_acls:
            add_validation(validations, "NETWORKING", "Network ACLs", "PASS", f"Detected {len(network_acls)} network ACL(s)")
        else:
            add_validation(validations, "NETWORKING", "Network ACLs", "WARNING", "No network ACLs detected")

        # MONITORING & MESSAGING
        if cloudwatch_client:
            try:
                metrics = cloudwatch_client.list_metrics().get("Metrics", [])
                add_validation(validations, "MONITORING & MESSAGING", "CloudWatch", "PASS" if metrics else "WARNING", f"metrics={len(metrics)}")
            except Exception as e:
                add_validation(validations, "MONITORING & MESSAGING", "CloudWatch", "UNABLE TO VERIFY", str(e))
            try:
                alarms = cloudwatch_client.describe_alarms().get("MetricAlarms", [])
                add_validation(validations, "MONITORING & MESSAGING", "CloudWatch Alarms", "PASS" if alarms else "WARNING", f"alarms={len(alarms)}")
            except Exception as e:
                add_validation(validations, "MONITORING & MESSAGING", "CloudWatch Alarms", "UNABLE TO VERIFY", str(e))
        else:
            add_validation(validations, "MONITORING & MESSAGING", "CloudWatch", "UNABLE TO VERIFY", "CloudWatch client unavailable")
            add_validation(validations, "MONITORING & MESSAGING", "CloudWatch Alarms", "UNABLE TO VERIFY", "CloudWatch client unavailable")

        if sns_client:
            try:
                topics = sns_client.list_topics().get("Topics", [])
                topic_arns = [topic.get("TopicArn") for topic in topics if topic.get("TopicArn")]
                add_validation(validations, "MONITORING & MESSAGING", "SNS", "PASS" if topic_arns else "WARNING", f"topics={len(topic_arns)}")
                subscriptions_total = 0
                subscription_query_failed = False
                for topic_arn in topic_arns:
                    try:
                        subscriptions_total += len(sns_client.list_subscriptions_by_topic(TopicArn=topic_arn).get("Subscriptions", []))
                    except Exception:
                        subscription_query_failed = True
                if subscription_query_failed:
                    add_validation(validations, "MONITORING & MESSAGING", "SNS subscription", "UNABLE TO VERIFY", "One or more topic subscription queries failed")
                elif subscriptions_total > 0:
                    add_validation(validations, "MONITORING & MESSAGING", "SNS subscription", "PASS", f"subscriptions={subscriptions_total}")
                else:
                    add_validation(validations, "MONITORING & MESSAGING", "SNS subscription", "WARNING", "No subscriptions detected")
            except Exception as e:
                add_validation(validations, "MONITORING & MESSAGING", "SNS", "UNABLE TO VERIFY", str(e))
                add_validation(validations, "MONITORING & MESSAGING", "SNS subscription", "UNABLE TO VERIFY", str(e))
        else:
            add_validation(validations, "MONITORING & MESSAGING", "SNS", "UNABLE TO VERIFY", "SNS client unavailable")
            add_validation(validations, "MONITORING & MESSAGING", "SNS subscription", "UNABLE TO VERIFY", "SNS client unavailable")

        # RELIABILITY summary checks.
        if asgs is None:
            add_validation(validations, "RELIABILITY", "ASG health check", "UNABLE TO VERIFY", "Unable to query ASGs")
        elif not asgs:
            add_validation(validations, "RELIABILITY", "ASG health check", "WARNING", "No ASGs detected")
        else:
            missing_elb_health = [asg.get("AutoScalingGroupName") for asg in asgs if asg.get("HealthCheckType") != "ELB"]
            if missing_elb_health:
                add_validation(validations, "RELIABILITY", "ASG health check", "WARNING", f"ASGs without ELB health check: {', '.join(missing_elb_health[:10])}")
            else:
                add_validation(validations, "RELIABILITY", "ASG health check", "PASS", "All ASGs use ELB health check")

        if subnets is None:
            add_validation(validations, "RELIABILITY", "Multi-AZ", "UNABLE TO VERIFY", "Unable to query subnets")
        else:
            multi_az_status = "PASS" if len({subnet.get("AvailabilityZone") for subnet in subnets if subnet.get("AvailabilityZone")}) > 1 else "WARNING"
            add_validation(validations, "RELIABILITY", "Multi-AZ", multi_az_status, "Based on subnet Availability Zones")

        # COST evidence checks.
        add_validation(
            validations,
            "COST",
            "Auto Scaling",
            "PASS" if asgs else ("UNABLE TO VERIFY" if asgs is None else "WARNING"),
            "Auto Scaling groups are available for right-sizing" if asgs else "No ASGs detected",
        )
        add_validation(
            validations,
            "COST",
            "Actual ALB count",
            "PASS" if lbs is not None else "UNABLE TO VERIFY",
            f"count={len(lbs)}" if lbs is not None else "Unable to query ALBs",
        )
        nat_count_details = "Unable to query NAT gateways" if nat_gateways is None else f"count={len([nat for nat in nat_gateways if nat.get('State') != 'deleted'])}"
        add_validation(
            validations,
            "COST",
            "Actual NAT Gateway count",
            "PASS" if nat_gateways is not None else "UNABLE TO VERIFY",
            nat_count_details,
        )

        # Render validation table with status-specific Streamlit feedback.
        for category, label, status, details in validations:
            message = f"{category} — {label}: {status} ({details})"
            if status == "PASS":
                st.success(message)
            elif status == "WARNING":
                st.warning(message)
            else:
                st.info(message)

        if network_acls:
            st.subheader("Network ACL Details")
            for nacl in network_acls[:10]:
                associated_subnet_ids = [assoc.get("SubnetId") for assoc in nacl.get("Associations", []) if assoc.get("SubnetId")]
                st.write(f"• NACL ID: {nacl.get('NetworkAclId')} | VPC ID: {nacl.get('VpcId')} | Associated Subnets: {associated_subnet_ids or ['N/A']}")
                inbound_entries = [entry for entry in nacl.get("Entries", []) if not entry.get("Egress")]
                outbound_entries = [entry for entry in nacl.get("Entries", []) if entry.get("Egress")]
                st.write("  Inbound rules:")
                if inbound_entries:
                    for entry in inbound_entries[:10]:
                        st.write(f"   - Rule {entry.get('RuleNumber')} | {entry.get('Protocol')} | {entry.get('RuleAction')} | CIDR {entry.get('CidrBlock') or entry.get('Ipv6CidrBlock') or 'N/A'}")
                else:
                    st.write("   - None")
                st.write("  Outbound rules:")
                if outbound_entries:
                    for entry in outbound_entries[:10]:
                        st.write(f"   - Rule {entry.get('RuleNumber')} | {entry.get('Protocol')} | {entry.get('RuleAction')} | CIDR {entry.get('CidrBlock') or entry.get('Ipv6CidrBlock') or 'N/A'}")
                else:
                    st.write("   - None")

        if target_health_rows:
            st.subheader("Target Group Health Details")
            for line in target_health_rows:
                st.write(f"• {line}")

        if asg_policy_summaries:
            st.subheader("ASG Policy Details")
            for row in asg_policy_summaries:
                st.write(f"• {row}")

        if section_errors:
            st.info("Some APIs could not be queried during this run:")
            for error_line in section_errors[:15]:
                st.info(f"• {error_line}")

        st.markdown("<div class='login-note'>This validation is evidence-based and does not automatically modify AWS infrastructure. Any unverified item is reported as UNABLE TO VERIFY.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Reliability & Recovery":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Reliability & recovery</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Review multi-AZ, failover, and backup-readiness posture.</div>", unsafe_allow_html=True)

        st.write("EC2 failure → ASG health check → replacement EC2 → ALB target registration → application remains available")
        st.write("• S3 versioning: review bucket state and enable if required")
        st.write("• EBS snapshots and AMIs: review manually in the AWS Console")
        st.write("• ALB and ASG health checks should be monitored together for a resilient architecture")
        st.write("• Multi-AZ architecture improves resilience while reducing blast radius")

        if not (ec2_client and elbv2_client and autoscaling_client and client):
            st.info("Connect to AWS first to load reliability evidence.")
        else:
            try:
                asgs = autoscaling_client.describe_auto_scaling_groups().get("AutoScalingGroups", [])
                lbs = elbv2_client.describe_load_balancers().get("LoadBalancers", [])
                target_groups = elbv2_client.describe_target_groups().get("TargetGroups", [])
                volumes = ec2_client.describe_volumes().get("Volumes", [])

                st.subheader("ASG")
                if asgs:
                    for asg in asgs:
                        st.write(
                            f"• {asg.get('AutoScalingGroupName')} | Min: {asg.get('MinSize')} | Desired: {asg.get('DesiredCapacity')} | Max: {asg.get('MaxSize')} | HealthCheck: {asg.get('HealthCheckType')} | AZ count: {len(set(asg.get('AvailabilityZones', [])))}"
                        )
                else:
                    st.warning("No Auto Scaling Groups detected.")

                st.subheader("ALB")
                if lbs:
                    for lb in lbs:
                        lb_arn = lb.get("LoadBalancerArn")
                        lb_target_groups = [tg.get("TargetGroupName") for tg in target_groups if tg.get("LoadBalancerArns") and lb_arn in tg.get("LoadBalancerArns", [])]
                        st.write(
                            f"• {lb.get('LoadBalancerName')} | AZ count: {len(lb.get('AvailabilityZones', []))} | DNS: {lb.get('DNSName')} | Target groups: {lb_target_groups or ['N/A']}"
                        )
                else:
                    st.warning("No ALBs detected.")

                st.subheader("Target Groups")
                if target_groups:
                    for tg in target_groups:
                        health = elbv2_client.describe_target_health(TargetGroupArn=tg.get("TargetGroupArn")).get("TargetHealthDescriptions", [])
                        registered = len(health)
                        healthy = len([entry for entry in health if entry.get("TargetHealth", {}).get("State") == "healthy"])
                        unhealthy = len([entry for entry in health if entry.get("TargetHealth", {}).get("State") in ["unhealthy", "draining", "unused", "unavailable", "initial"]])
                        st.write(f"• {tg.get('TargetGroupName')} | Registered targets: {registered} | Healthy targets: {healthy} | Unhealthy targets: {unhealthy}")
                else:
                    st.warning("No target groups detected.")

                st.subheader("S3 Versioning")
                if bucket_names:
                    for bucket_name in bucket_names:
                        try:
                            versioning_status = client.get_bucket_versioning(Bucket=bucket_name).get("Status", "Not Enabled")
                            st.write(f"• {bucket_name}: {versioning_status}")
                        except Exception as e:
                            st.info(f"• {bucket_name}: UNABLE TO VERIFY ({e})")
                else:
                    st.warning("No S3 buckets detected.")

                st.subheader("EC2 EBS Encryption")
                if volumes:
                    for volume in volumes[:20]:
                        st.write(f"• {volume.get('VolumeId')} | Encrypted: {volume.get('Encrypted')} | State: {volume.get('State')} | Instance: {volume.get('Attachments', [{}])[0].get('InstanceId', 'N/A')}")
                else:
                    st.warning("No EBS volumes detected.")
            except Exception as e:
                st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Cost Optimization":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Cost optimization</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Useful configuration summary for AWS Pricing Calculator input.</div>", unsafe_allow_html=True)

        ec2_instances = []
        ec2_instance_types = []
        asgs = []
        total_asg_min = 0
        total_asg_desired = 0
        total_asg_max = 0
        alb_count = 0
        nat_gateway_count = 0

        try:
            if ec2_client:
                reservations = ec2_client.describe_instances().get("Reservations", [])
                for reservation in reservations:
                    for instance in reservation.get("Instances", []):
                        ec2_instances.append(instance)
                ec2_instance_types = sorted({instance.get("InstanceType") for instance in ec2_instances if instance.get("InstanceType")})
        except Exception:
            ec2_instances = []

        try:
            if autoscaling_client:
                asgs = autoscaling_client.describe_auto_scaling_groups().get("AutoScalingGroups", [])
                total_asg_min = sum(int(asg.get("MinSize", 0)) for asg in asgs)
                total_asg_desired = sum(int(asg.get("DesiredCapacity", 0)) for asg in asgs)
                total_asg_max = sum(int(asg.get("MaxSize", 0)) for asg in asgs)
        except Exception:
            asgs = []

        try:
            if elbv2_client:
                alb_count = len(elbv2_client.describe_load_balancers().get("LoadBalancers", []))
        except Exception:
            alb_count = 0

        try:
            if ec2_client and hasattr(ec2_client, "describe_nat_gateways"):
                nat_gateways = ec2_client.describe_nat_gateways().get("NatGateways", [])
                nat_gateway_count = len([nat for nat in nat_gateways if nat.get("State") != "deleted"])
        except Exception:
            nat_gateway_count = 0

        pricing_summary = f"""AWS Pricing Calculator Input Summary
Region: {st.session_state.connected_region or 'unknown'}
EC2 instance count: {len(ec2_instances)}
EC2 instance type(s): {', '.join(ec2_instance_types) if ec2_instance_types else 'N/A'}
ASG count: {len(asgs)}
ASG minimum capacity total: {total_asg_min}
ASG desired capacity total: {total_asg_desired}
ASG maximum capacity total: {total_asg_max}
ALB count: {alb_count}
S3 buckets: {len(bucket_names)}
NAT Gateway count: {nat_gateway_count}
CloudWatch: enabled
Lambda functions: {len(lambda_client.list_functions().get('Functions', [])) if lambda_client else 0}
DynamoDB tables: {len(dynamodb_client.list_tables().get('TableNames', [])) if dynamodb_client else 0}
SNS topics: {len(sns_client.list_topics().get('Topics', [])) if sns_client else 0}

Recommendations:
- Auto Scaling reduces unnecessary EC2 capacity and supports burst demand.
- Right-size EC2 instance types based on workload usage.
- Use S3 lifecycle policies to reduce storage cost.
- Review NAT Gateway usage in low-traffic designs.
- Monitor Lambda and CloudWatch usage to remove idle resources.
"""

        st.code(pricing_summary, language="text")

        if st.button("Generate Pricing Calculator Input Summary"):
            st.text_area("Pricing Calculator Summary", pricing_summary, height=350)

        st.write("• Auto Scaling to avoid unnecessary EC2 capacity")
        st.write("• Right-size EC2 instances and eliminate overprovisioning")
        st.write("• S3 lifecycle policies and retention cleanup")
        st.write("• Manage NAT Gateway usage and private/public subnet design")

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Extended Report":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Extended resource report</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Generate a broader AWS resource summary covering storage, compute, monitoring, security, and audit activity.</div>", unsafe_allow_html=True)

        if not bucket_names:
            st.info("No buckets available for report export.")
        else:
            report_bucket = st.selectbox("Select bucket for export", bucket_names, key="extended_report_bucket")
            if st.button("Generate extended report"):
                try:
                    report_lines = []
                    report_lines.append("AWS EXTENDED RESOURCE REPORT")
                    report_lines.append("=" * 70)
                    report_lines.append(f"Region: {st.session_state.connected_region or 'unknown'}")
                    report_lines.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
                    report_lines.append("")

                    report_lines.append("S3 BUCKETS")
                    report_lines.append("-" * 70)
                    for bucket_name in bucket_names:
                        report_lines.append(f"Bucket: {bucket_name}")
                    report_lines.append("")

                    report_lines.append("EC2 INSTANCES")
                    report_lines.append("-" * 70)
                    ec2_response = ec2_client.describe_instances()
                    for reservation in ec2_response.get("Reservations", []):
                        for instance in reservation.get("Instances", []):
                            report_lines.append(f"Instance: {instance.get('InstanceId')} | Type: {instance.get('InstanceType')} | State: {instance.get('State', {}).get('Name')} | AZ: {instance.get('Placement', {}).get('AvailabilityZone')}")
                    report_lines.append("")

                    report_lines.append("CLOUDWATCH")
                    report_lines.append("-" * 70)
                    if cloudwatch_client:
                        metrics = cloudwatch_client.list_metrics().get("Metrics", [])
                        report_lines.append(f"CloudWatch metrics discovered: {len(metrics)}")
                    else:
                        report_lines.append("CloudWatch client unavailable")
                    report_lines.append("")

                    report_lines.append("IAM AND SECURITY")
                    report_lines.append("-" * 70)
                    if iam_client:
                        report_lines.append(f"IAM users: {len(iam_client.list_users().get('Users', []))}")
                        report_lines.append(f"IAM roles: {len(iam_client.list_roles().get('Roles', []))}")
                    report_lines.append(f"Security groups: {len(ec2_client.describe_security_groups().get('SecurityGroups', []))}")
                    report_lines.append("")

                    report_lines.append("AUDIT LOG")
                    report_lines.append("-" * 70)
                    events = load_audit_events()
                    for event in events[-10:]:
                        report_lines.append(f"{event.get('timestamp')} - {event.get('message')}")

                    filename = "aws_extended_resource_report.txt"
                    report_text = "\n".join(report_lines)
                    with open(filename, "w", encoding="utf-8") as file_obj:
                        file_obj.write(report_text)

                    client.upload_file(filename, report_bucket, filename)
                    append_log(f"Generated and uploaded extended report to {report_bucket}")
                    st.success("Extended report generated and uploaded.")
                    st.text_area("Extended report preview", report_text, height=400)
                except Exception as e:
                    st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Question 5 - Report":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Resource Report</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Generate report and upload it to S3.</div>", unsafe_allow_html=True)

        if not bucket_names:
            st.info("No buckets available.")
        else:
            report_bucket = st.selectbox(
                "Select Bucket for Report Upload",
                bucket_names,
                key="report_bucket"
            )

            if st.button("Generate Resource Report"):
                try:
                    report_lines = []
                    report_lines.append("AWS RESOURCE REPORT")
                    report_lines.append("=" * 60)

                    report_lines.append("\nS3 BUCKET DETAILS")
                    report_lines.append(f"Bucket Name: {report_bucket}")
                    report_lines.append("-" * 60)

                    response = client.list_objects_v2(Bucket=report_bucket)

                    if "Contents" in response:
                        for obj in response["Contents"]:
                            key = obj["Key"]
                            size = obj["Size"]

                            folder = key.split("/")[0] if "/" in key else "root"

                            report_lines.append(f"Folder Name : {folder}")
                            report_lines.append(f"Object Name : {key}")
                            report_lines.append(f"Object Size : {size} bytes")
                            report_lines.append("-" * 40)
                    else:
                        report_lines.append("Bucket is empty.")

                    report_lines.append("\nEC2 INSTANCE DETAILS")
                    report_lines.append("-" * 60)

                    ec2_response = ec2_client.describe_instances()
                    found = False

                    for reservation in ec2_response["Reservations"]:
                        for instance in reservation["Instances"]:
                            if instance["State"]["Name"] == "running":
                                found = True

                                instance_id = instance["InstanceId"]
                                instance_type = instance["InstanceType"]
                                state = instance["State"]["Name"]
                                public_ip = instance.get("PublicIpAddress", "N/A")
                                az = instance["Placement"]["AvailabilityZone"]

                                name = "N/A"
                                if "Tags" in instance:
                                    for tag in instance["Tags"]:
                                        if tag["Key"] == "Name":
                                            name = tag["Value"]

                                report_lines.append(f"Instance ID   : {instance_id}")
                                report_lines.append(f"Instance Name : {name}")
                                report_lines.append(f"Instance Type : {instance_type}")
                                report_lines.append(f"State         : {state}")
                                report_lines.append(f"Public IP     : {public_ip}")
                                report_lines.append(f"AZ            : {az}")
                                report_lines.append("-" * 40)

                    if not found:
                        report_lines.append("No running EC2 instances found.")

                    filename = "aws_resource_report.txt"
                    report_text = "\n".join(report_lines)

                    with open(filename, "w") as f:
                        f.write(report_text)

                    client.upload_file(
                        filename,
                        report_bucket,
                        filename
                    )

                    st.success("✅ Report generated and uploaded successfully!")

                    append_log(
                        f"Generated and uploaded {filename} to {report_bucket}"
                    )

                    verify = client.list_objects_v2(Bucket=report_bucket)
                    uploaded = False

                    if "Contents" in verify:
                        for obj in verify["Contents"]:
                            if obj["Key"] == filename:
                                uploaded = True
                                break

                    if uploaded:
                        st.success("✅ Upload verification successful!")
                    else:
                        st.error("Upload verification failed.")

                    st.subheader("Report Preview")
                    st.text_area(
                        "AWS Resource Report",
                        report_text,
                        height=450
                    )

                except Exception as e:
                    st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    elif active_section == "Activity Logs":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Activity log</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Recent actions are preserved for the current session.</div>", unsafe_allow_html=True)
        if st.session_state.logs:
            for log_entry in reversed(st.session_state.logs):
                st.write(f"• {log_entry}")
        else:
            st.info("No activity yet.")
        st.markdown("</div>", unsafe_allow_html=True)
