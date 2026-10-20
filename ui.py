import time, requests, streamlit as st
st.set_page_config(page_title="B-roll Studio",page_icon="🎬",layout="wide")
st.title("🎬 Script & Voiceover to B-roll Studio")
st.caption("IncuBrix Software Engineer Assessment · PS3 prototype")
base=st.sidebar.text_input("API base URL", "http://localhost:8000").rstrip('/')
mode=st.radio("Input type",["Script to video","Upload voiceover"],horizontal=True)
ratios=st.multiselect("Output aspect ratios",["16:9","9:16","1:1"],default=["16:9"])
style=st.text_input("Visual style", "bright, modern, real-world footage")
if mode=="Script to video":
    script=st.text_area("Narration script",height=220,placeholder="Write a few sentences. Each sentence becomes a scene.")
    voice=st.selectbox("Narration voice",["en-IN-female","en-IN-male","en-US-female","en-US-male"])
    if st.button("Generate video",type="primary",disabled=not script.strip() or not ratios):
        try:
            r=requests.post(base+"/api/v1/broll/jobs",json={"script":script,"voice":voice,"aspect_ratios":ratios,"style":style,"captions":{"burn_in":True,"srt":True}},headers={"Idempotency-Key":f"ui-{time.time_ns()}"},timeout=30)
            r.raise_for_status(); st.session_state.job_id=r.json()["job_id"]
        except Exception as e: st.error(f"Could not start job: {e}")
else:
    audio=st.file_uploader("Upload MP3, WAV or M4A",type=["mp3","wav","m4a"])
    if st.button("Generate video",type="primary",disabled=audio is None or not ratios):
        try:
            r=requests.post(base+"/api/v1/broll/jobs/upload",files={"file":(audio.name,audio.getvalue(),audio.type or "application/octet-stream")},data={"aspect_ratios":__import__('json').dumps(ratios),"style":style},headers={"Idempotency-Key":f"ui-{time.time_ns()}"},timeout=60)
            r.raise_for_status(); st.session_state.job_id=r.json()["job_id"]
        except Exception as e: st.error(f"Could not start job: {e}")
if st.session_state.get("job_id"):
    jid=st.session_state.job_id
    if st.button("Refresh job status"): st.rerun()
    try:
        job=requests.get(base+f"/api/v1/jobs/{jid}",timeout=10).json()
        st.write(f"Job ID: `{jid}` · Status: **{job['status']}**")
        st.progress(job.get("progress",0)/100)
        if job['status']=="failed": st.error(job.get('error'))
        elif job['status']=="succeeded":
            st.success("Video generation finished")
            for video in job['result']['videos']:
                url=base+video['download_url']; st.subheader(video['aspect_ratio']); st.video(url); st.markdown(f"[Download MP4]({url})")
            for label,key in [("Captions","captions_url"),("Timeline JSON","timeline_url"),("Manifest JSON","manifest_url")]:
                st.markdown(f"[{label}]({base+job['result'][key]})")
        else: st.info("Job is processing. Refresh in a few seconds.")
    except Exception as e: st.warning(f"Could not read job status: {e}")
