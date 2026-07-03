
import boto3
import streamlit as st


st.set_page_config(page_title="S3 Manager", page_icon="☁", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at 18% 18%, rgba(37, 99, 235, 0.22), transparent 0 24%),
                radial-gradient(circle at 82% 22%, rgba(14, 165, 233, 0.14), transparent 0 22%),
                linear-gradient(135deg, #081120 0%, #0f172a 45%, #111827 100%);
            color: #e5eefc;
        }
        .login-shell {
            min-height: 76vh;
            display: flex;
            align-items: center; 
            justify-content: center;
        }
        .login-card {
            width: min(540px, 100%);
            padding: 2.2rem;
            border-radius: 30px;
            background:
                linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.84)),
                rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(148, 163, 184, 0.22);
            box-shadow: 0 28px 80px rgba(2, 6, 23, 0.42);
            backdrop-filter: blur(18px);
            position: relative;
            overflow: hidden;
        }
        .login-copy-card {
            width: min(540px, 100%);
            padding: 2.2rem;
            border-radius: 30px;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.82));
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: 0 28px 80px rgba(2, 6, 23, 0.34);
            color: #e2e8f0;
            position: relative;
            overflow: hidden;
        }
        .login-copy-card:before {
            content: "";
            position: absolute;
            inset: auto -12% -18% auto;
            width: 240px;
            height: 240px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(56, 189, 248, 0.18), transparent 68%);
            pointer-events: none;
        }
        .login-card:before {
            content: "";
            position: absolute;
            inset: -35% -10% auto auto;
            width: 220px;
            height: 220px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(56, 189, 248, 0.22), transparent 68%);
            pointer-events: none;
        }
        .login-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.16);
            color: #bfdbfe;
            font-size: 0.84rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }
        .login-title {
            margin: 1rem 0 0;
            font-size: clamp(2rem, 3vw, 2.6rem);
            line-height: 1.02;
            letter-spacing: -0.04em;
            color: #f8fafc;
        }
        .login-subtitle {
            margin: 0.85rem 0 0;
            color: #cbd5e1;
            line-height: 1.7;
            max-width: 34rem;
        }
        .login-note {
            margin-top: 1rem;
            padding: 0.9rem 1rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(148, 163, 184, 0.16);
            color: #dbeafe;
            font-size: 0.94rem;
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.35rem;
        }
        .section-subtitle {
            color: #64748b;
            margin-bottom: 1rem;
        }
        [data-testid="stMetricValue"] {
            color: #0f172a;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        }
        [data-testid="stSidebar"] * {
            color: #e5e7eb;
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
        .stTextInput label {
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
        .dashboard-headline {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.5rem 0.8rem;
            border-radius: 999px;
            background: rgba(16, 185, 129, 0.12);
            color: #047857;
            font-weight: 700;
            font-size: 0.9rem;
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

with st.sidebar:
    if st.session_state.client:
        st.markdown("### Connection")
        st.markdown("<span class='status-badge'>● Connected</span>", unsafe_allow_html=True)
        st.caption(f"Region: {st.session_state.connected_region or 'unknown'}")
        if st.button("Disconnect", use_container_width=True):
            st.session_state.client = None
            st.session_state.connected_region = None
            st.session_state.ec2_client = None
            append_log("Disconnected from AWS")
            st.rerun()


client = st.session_state.client
ec2_client = st.session_state.ec2_client

if not client:
    st.markdown("<div class='login-shell'>", unsafe_allow_html=True)
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("<div class='login-copy-card'>", unsafe_allow_html=True)
        st.markdown("<span class='login-badge'>AWS S3 access</span>", unsafe_allow_html=True)
        st.markdown("<h2 class='login-title'>Sign in to S3 Manager</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p class='login-subtitle'>Enter your AWS credentials below to open the dashboard. The app stays on this page until the connection is verified.</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='login-note'>Use your access key, secret key, and optional session token to continue.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<h2 class='login-title'>Credentials</h2>", unsafe_allow_html=True)
        st.markdown("<p class='login-subtitle'>Fill in your AWS details to continue.</p>", unsafe_allow_html=True)
        with st.form("aws_connect_form", clear_on_submit=False):
            ak = st.text_input("Access Key", placeholder="AKIAxxxxxxxxxxxxxxxx", type="password")
            sk = st.text_input("Secret Key", placeholder="Paste your secret access key", type="password")
            tk = st.text_input("Session Token", placeholder="Optional: temporary session token", type="password")
            region = st.selectbox("Region", ["us-east-1", "ap-south-1", "us-west-1"])
            submitted = st.form_submit_button("Connect to AWS", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        try:
            client = boto3.client(
                "s3",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=tk or None,
                region_name=region,
            )
            ec2_client = boto3.client(
                "ec2",
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                aws_session_token=tk or None,
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
        """
        <div class="dashboard-headline">
            <div>
                <h1 style="margin:0;color:#0f172a;font-size:2.2rem;">S3 Manager Dashboard</h1>
                <p style="margin:0.4rem 0 0;color:#475569;">Connected workspace for bucket operations and access control.</p>
            </div>
            <div class="status-badge">● Live AWS session</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Buckets", total_buckets)
    metric_col2.metric("Objects sampled", total_objects)
    metric_col3.metric("Region", st.session_state.connected_region or "unknown")
    metric_col4.metric("Activity events", len(st.session_state.logs))

    tabs = st.tabs(["Overview", "Create Bucket", "Upload Files", "Manage Access", "Question 4 - EC2",
    "Question 5 - Report", "Activity Logs"])

    with tabs[0]:
        overview_col1, overview_col2 = st.columns([1.1, 0.9])
        with overview_col1:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Bucket inventory</div>", unsafe_allow_html=True)
            st.markdown("<div class='section-subtitle'>A quick snapshot of your current S3 footprint.</div>", unsafe_allow_html=True)
            if bucket_names:
                for bucket_name in bucket_names:
                    st.write(f"• {bucket_name}")
            else:
                st.info("No buckets found yet.")
            st.markdown("</div>", unsafe_allow_html=True)
        with overview_col2:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Workflow</div>", unsafe_allow_html=True)
            st.markdown("<div class='section-subtitle'>Use the tabs to perform actions in a deliberate order.</div>", unsafe_allow_html=True)
            st.write("1. Create or select a bucket.")
            st.write("2. Upload one or more files.")
            st.write("3. Adjust ACLs for specific objects.")
            st.markdown("</div>", unsafe_allow_html=True)

    with tabs[1]:
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

    with tabs[2]:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Upload files</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Upload files into ufolder or efolder inside the selected bucket.</div>",
            unsafe_allow_html=True
        )

        if not bucket_names:
            st.info("Create a bucket first to enable uploads.")
        else:
            with st.form("upload_form"):
                selected_bucket = st.selectbox(
                    "Select Bucket",
                    bucket_names,
                    key="upload_bucket"
                )

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
                        # Create folders if they don't exist
                        client.put_object(Bucket=selected_bucket, Key="ufolder/")
                        client.put_object(Bucket=selected_bucket, Key="efolder/")

                        # Upload into chosen folder
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

                        # List all objects in bucket
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
    with tabs[3]:
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

    with tabs[4]:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Question 4 - EC2 Instance Details</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Retrieve all running EC2 instances.</div>",
            unsafe_allow_html=True
        )

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


    with tabs[5]:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Question 5 - AWS Resource Report</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Generate report and upload it to S3.</div>",
            unsafe_allow_html=True
        )

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

                    # ======================
                    # S3 DETAILS
                    # ======================
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

                    # ======================
                    # EC2 DETAILS
                    # ======================
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

                    # ======================
                    # WRITE REPORT
                    # ======================
                    filename = "aws_resource_report.txt"
                    report_text = "\n".join(report_lines)

                    with open(filename, "w") as f:
                        f.write(report_text)

                    # ======================
                    # UPLOAD REPORT TO S3
                    # ======================
                    client.upload_file(
                        filename,
                        report_bucket,
                        filename
                    )

                    st.success("✅ Report generated and uploaded successfully!")

                    append_log(
                        f"Generated and uploaded {filename} to {report_bucket}"
                    )

                    # Verify upload
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

    with tabs[6]:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>Activity log</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Recent actions are preserved for the current session.</div>", unsafe_allow_html=True)
        if st.session_state.logs:
            for log_entry in reversed(st.session_state.logs):
                st.write(f"• {log_entry}")
        else:
            st.info("No activity yet.")
        st.markdown("</div>", unsafe_allow_html=True)
