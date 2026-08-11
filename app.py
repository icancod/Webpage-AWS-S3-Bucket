
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
    st.session_state.logs.append(message)


if "client" not in st.session_state:
    st.session_state.client = None
if "logs" not in st.session_state:
    st.session_state.logs = []
if "connected_region" not in st.session_state:
    st.session_state.connected_region = None
if "ec2_client" not in st.session_state:
    st.session_state.ec2_client = None
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
        "Reporting",
        [
            ("◦ Resource Report", "Question 5 - Report"),
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
    "Question 5 - Report": ("Reporting", "Resource Report", "Generate and upload an AWS resource report to S3."),
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
            st.session_state.active_section = "Overview"
            append_log("Disconnected from AWS")
            st.rerun()


client = st.session_state.client
ec2_client = st.session_state.ec2_client

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
            client.list_buckets()
            st.session_state.client = client
            st.session_state.ec2_client = ec2_client
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
