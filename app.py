
import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="نظام تحليل الاحتياجات التدريبية",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

LIKERT = {"منخفض جدًا": 1, "منخفض": 2, "متوسط": 3, "مرتفع": 4, "مرتفع جدًا": 5}
USAGE = {"نادرًا": 1, "أحيانًا": 2, "غالبًا": 3, "دائمًا": 4}

READINESS_ITEMS = [
    "أمتلك معرفة أساسية بمفاهيم الذكاء الاصطناعي.",
    "أستطيع استخدام أدوات الذكاء الاصطناعي في عملي.",
    "أميز بين الاستخدام الآمن وغير الآمن للذكاء الاصطناعي.",
    "أستطيع تقييم مخرجات أدوات الذكاء الاصطناعي.",
]
USAGE_ITEM = "هل تستخدم أدوات الذكاء الاصطناعي في عملك؟"
NEEDS_ITEM = "ما المجالات التي تحتاج إلى تدريب فيها؟"

TRAINING_GUIDE = {
    "أساسيات الذكاء الاصطناعي": ("AI Foundations", "OpenAI Academy", "https://academy.openai.com/"),
    "هندسة الأوامر (Prompt Engineering)": ("Prompting Fundamentals", "OpenAI Academy", "https://openai.com/academy/prompting/"),
    "Microsoft Copilot": ("Get started with Microsoft 365 Copilot", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/get-started-with-microsoft-365-copilot/"),
    "تصميم الصور والفيديو": ("Work smarter with AI", "Canva Design School", "https://www.canva.com/design-school/courses/work-smarter-with-ai"),
    "تحليل البيانات": ("Foundations: Data, Data, Everywhere", "Google Skills", "https://www.skills.google/paths/2267/course_templates/1222"),
    "تصميم المحتوى التعليمي": ("Generative AI for Educators with Gemini", "Google for Education", "https://grow.google/ai-for-educators/"),
    "الاستخدام الآمن والأخلاقي للذكاء الاصطناعي": ("Responsible use of AI in education", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/responsible-use-of-artificial-intelligence-in-education/"),
}

PATH_DIAGNOSIS = {
    "المسار التأسيسي": "يحتاج إلى تعزيز المعارف والمهارات الأساسية في توظيف الذكاء الاصطناعي.",
    "المسار التطويري": "يمتلك أساسًا جيدًا ويحتاج إلى توسيع الاستخدام العملي وتطوير مهاراته التطبيقية.",
    "المسار التطبيقي المتقدم": "يمتلك جاهزية وخبرة جيدة، ويستفيد من التدريب المتقدم في مجالات تطبيقية متخصصة.",
}

def readiness_level(score):
    if score < 50:
        return "منخفض"
    if score < 70:
        return "متوسط"
    if score < 85:
        return "مرتفع"
    return "مرتفع جدًا"

def usage_level(score):
    return {1: "محدود", 2: "متوسط", 3: "مرتفع", 4: "مكثف"}.get(score, "")

def training_path(readiness, usage):
    if readiness == "منخفض":
        return "المسار التأسيسي"
    if readiness == "متوسط":
        return "المسار التأسيسي" if usage in ["محدود", "متوسط"] else "المسار التطويري"
    if readiness == "مرتفع":
        return "المسار التطويري" if usage in ["محدود", "متوسط"] else "المسار التطبيقي المتقدم"
    return "المسار التطويري" if usage == "محدود" else "المسار التطبيقي المتقدم"

def split_needs(value):
    if pd.isna(value):
        return []
    return [item.strip() for item in str(value).split(";") if item.strip()]

def analyze(df):
    result = df.copy()

    score_cols = []
    for i, question in enumerate(READINESS_ITEMS, 1):
        col = f"_readiness_{i}"
        result[col] = result[question].map(LIKERT)
        score_cols.append(col)

    result["مؤشر الجاهزية (%)"] = (result[score_cols].mean(axis=1) * 20).round(1)
    result["مستوى الجاهزية"] = result["مؤشر الجاهزية (%)"].apply(readiness_level)

    result["_usage_score"] = result[USAGE_ITEM].map(USAGE)
    result["مستوى الاستخدام"] = result["_usage_score"].apply(usage_level)

    result["المسار التدريبي المقترح"] = [
        training_path(r, u)
        for r, u in zip(result["مستوى الجاهزية"], result["مستوى الاستخدام"])
    ]

    needs = result[NEEDS_ITEM].apply(split_needs)
    result["الأولوية التدريبية الأولى"] = needs.apply(lambda x: x[0] if x else "")
    result["الأولوية التدريبية الثانية"] = needs.apply(lambda x: x[1] if len(x) > 1 else "")

    result["التشخيص المختصر"] = result["المسار التدريبي المقترح"].map(PATH_DIAGNOSIS)

    for n, priority_col in [(1, "الأولوية التدريبية الأولى"), (2, "الأولوية التدريبية الثانية")]:
        result[f"البرنامج التدريبي المقترح {n}"] = result[priority_col].apply(
            lambda x: TRAINING_GUIDE.get(x, ("", "", ""))[0]
        )
        result[f"منصة التدريب {n}"] = result[priority_col].apply(
            lambda x: TRAINING_GUIDE.get(x, ("", "", ""))[1]
        )
        result[f"رابط التدريب {n}"] = result[priority_col].apply(
            lambda x: TRAINING_GUIDE.get(x, ("", "", ""))[2]
        )

    def recommendation(row):
        text = f'{row["التشخيص المختصر"]} يُوصى بالالتحاق بـ{row["المسار التدريبي المقترح"]}.'
        need = row["الأولوية التدريبية الأولى"]
        program = row["البرنامج التدريبي المقترح 1"]
        platform = row["منصة التدريب 1"]
        if need and program and platform:
            text += f' الأولوية التدريبية: {need}. ويُقترح برنامج «{program}» على منصة {platform}.'
        return text

    result["التوصية التدريبية الفردية"] = result.apply(recommendation, axis=1)
    return result.drop(columns=score_cols + ["_usage_score"])

def to_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="نتائج التحليل", index=False)

        readiness = df["مستوى الجاهزية"].value_counts().rename_axis("مستوى الجاهزية").reset_index(name="العدد")
        paths = df["المسار التدريبي المقترح"].value_counts().rename_axis("المسار التدريبي").reset_index(name="العدد")

        all_needs = []
        for value in df[NEEDS_ITEM].fillna(""):
            all_needs.extend(split_needs(value))
        needs = pd.Series(all_needs).value_counts().rename_axis("الاحتياج التدريبي").reset_index(name="العدد")

        readiness.to_excel(writer, sheet_name="ملخص الجاهزية", index=False)
        paths.to_excel(writer, sheet_name="ملخص المسارات", index=False)
        needs.to_excel(writer, sheet_name="ملخص الاحتياجات", index=False)

    return output.getvalue()

st.markdown("""
<style>
html, body, [class*="css"] { direction: rtl; text-align: right; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
div[data-testid="stMetric"] { background: #f7f9fc; border: 1px solid #e6eaf0; padding: 12px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 نظام الذكاء الاصطناعي لتحليل الاحتياجات التدريبية")
st.caption("ضمن مشروع «نحو تعلم ذكي ومستدام»")

if "results" not in st.session_state:
    st.session_state.results = None

page = st.sidebar.radio(
    "التنقل",
    ["الرئيسية", "رفع وتحليل البيانات", "لوحة النتائج", "نتائج المعلمين", "دليل الاستخدام"],
)

if page == "الرئيسية":
    st.subheader("من الاستبانة إلى توصية تدريبية واضحة")
    st.write(
        "يقوم النظام بتحليل نتائج استبانة جاهزية المعلمين، واحتساب مؤشر الجاهزية، "
        "وتحديد مستوى الاستخدام والمسار التدريبي والاحتياجات والبرامج التدريبية المقترحة."
    )
    st.info("ابدأ من «رفع وتحليل البيانات»، ثم استعرض لوحة النتائج ونتائج المعلمين.")

elif page == "رفع وتحليل البيانات":
    st.subheader("رفع ملف نتائج الاستبانة")
    uploaded = st.file_uploader("اختر ملف Excel بصيغة xlsx", type=["xlsx"])

    if uploaded is not None:
        try:
            df = pd.read_excel(uploaded)
            st.success(f"تم تحميل الملف بنجاح — عدد الاستجابات: {len(df)}")

            required = READINESS_ITEMS + [USAGE_ITEM, NEEDS_ITEM]
            missing = [c for c in required if c not in df.columns]

            if missing:
                st.error("تعذر التحليل لأن بعض أعمدة الاستبانة المطلوبة غير موجودة.")
                with st.expander("عرض الأعمدة المفقودة"):
                    st.write(missing)
            else:
                if st.button("تحليل البيانات", type="primary", use_container_width=True):
                    st.session_state.results = analyze(df)
                    st.success("اكتمل التحليل بنجاح.")
        except Exception as exc:
            st.error(f"تعذر قراءة الملف: {exc}")

elif page == "لوحة النتائج":
    result = st.session_state.results
    if result is None:
        st.warning("يرجى رفع ملف الاستبانة وتحليله أولًا.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("عدد المشاركين", len(result))
        c2.metric("متوسط الجاهزية", f'{result["مؤشر الجاهزية (%)"].mean():.1f}%')
        c3.metric("المسار الأكثر شيوعًا", result["المسار التدريبي المقترح"].mode().iloc[0])
        c4.metric("عدد البرامج المقترحة", result["البرنامج التدريبي المقترح 1"].nunique())

        st.subheader("توزيع المسارات التدريبية")
        st.bar_chart(result["المسار التدريبي المقترح"].value_counts())

        st.subheader("أعلى الاحتياجات التدريبية")
        all_needs = []
        for value in result[NEEDS_ITEM].fillna(""):
            all_needs.extend(split_needs(value))
        if all_needs:
            st.bar_chart(pd.Series(all_needs).value_counts().head(7))

        st.download_button(
            "⬇️ تنزيل نتائج التحليل Excel",
            data=to_excel_bytes(result),
            file_name="نتائج_تحليل_الاحتياجات_التدريبية.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

elif page == "نتائج المعلمين":
    result = st.session_state.results
    if result is None:
        st.warning("يرجى رفع ملف الاستبانة وتحليله أولًا.")
    else:
        name_col = "Name" if "Name" in result.columns else result.columns[0]
        search = st.text_input("البحث باسم المعلم")
        path_filter = st.selectbox(
            "تصفية حسب المسار",
            ["الكل"] + sorted(result["المسار التدريبي المقترح"].dropna().unique().tolist())
        )

        view = result.copy()
        if search:
            view = view[view[name_col].astype(str).str.contains(search, case=False, na=False)]
        if path_filter != "الكل":
            view = view[view["المسار التدريبي المقترح"] == path_filter]

        display_cols = [
            name_col,
            "مؤشر الجاهزية (%)",
            "مستوى الجاهزية",
            "مستوى الاستخدام",
            "المسار التدريبي المقترح",
            "الأولوية التدريبية الأولى",
            "البرنامج التدريبي المقترح 1",
            "منصة التدريب 1",
            "رابط التدريب 1",
            "التوصية التدريبية الفردية",
        ]
        st.dataframe(view[display_cols], use_container_width=True, hide_index=True)

elif page == "دليل الاستخدام":
    st.subheader("دليل الاستخدام")
    st.markdown("""
1. صدّر نتائج الاستبانة من Microsoft Forms بصيغة Excel.
2. افتح صفحة **رفع وتحليل البيانات**.
3. ارفع ملف Excel واضغط **تحليل البيانات**.
4. استعرض **لوحة النتائج**.
5. افتح **نتائج المعلمين** للبحث والتصفية.
6. نزّل ملف النتائج النهائي من لوحة النتائج.
    """)
    st.caption("لا يحتاج المستخدم النهائي إلى تثبيت Python أو أي برنامج إضافي عند نشر التطبيق على الويب.")
