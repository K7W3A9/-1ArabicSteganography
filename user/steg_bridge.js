/**
 * 🔒 STEG_ARABIC - البروتوكول الأمني للربط بين الواجهات والخادم الخلفي
 * مشروع تخرج: نظام التضمين والتعمية المزدوجة للنصوص العربية داخل الصور
 * هندسة الأمن السيبراني والمعلومات
 */

 console.log("%c[STEG-ARABIC] 🛡️ تم تحميل بروتوكول الربط الأمني الذكي بنجاح.", "color: #3b82f6; font-weight: bold; font-size: 13px;");

 // 1. الوصول السريع لبيانات نظام ومحرك Alpine.js الحركي
 function getCyberContext() {
     const root = document.querySelector('[x-data]');
     if (root && root.__x && root.__x.$data) {
         return root.__x.$data;
     }
     return window.Alpine ? window.Alpine.$data(root) : null;
 }
 
 // 2. محرك فحص سعة البكسلات التلقائي (Capacity Analyzer)
 window.checkImageCapacity = async function(file) {
     const ctx = getCyberContext();
     if (!file) return;
     
     try {
         const formData = new FormData();
         formData.append('image', file);
         
         const response = await fetch('/check_capacity', { method: 'POST', body: formData });
         if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
         
         const data = await response.json();
         
         if (data.status === 'success') {
             if (ctx) {
                 ctx.maxChars = data.chars;
                 ctx.capacityBits = data.bits;
                 ctx.triggerToast(`تحليل البكسلات: الحاضن جاهز ويتسع لـ ${data.chars} حرفاً عربياً مشفراً.`, 'info');
             }
             console.log(`%c[ANALYZER] سعة الصورة المكتشفة: ${data.chars} محرف.`, "color: #10b981;");
         } else {
             if (ctx) ctx.triggerToast(data.message || 'فشل فحص بنية الصورة.', 'error');
         }
     } catch (error) {
         console.error("[ANALYZER ERROR]", error);
         if (ctx) ctx.triggerToast('فشل نظام الفحص الإحصائي في تحديد أبعاد الصورة الرقمية.', 'error');
     }
 };
 
 // 3. آلية تنفيذ معالجة التضمين (Core Embedding Logic) - مع دعم التحميل اليدوي والمقارنة
 window.runEmbed = async function() {
     const ctx = getCyberContext();
     if (!ctx) {
         console.error("[CRITICAL] لم يتم العثور على سياق واجهة Alpine.js.");
         return;
     }
     
     const fileInput = document.querySelector('[x-ref="embedFile"]');
     if (!fileInput || !fileInput.files[0]) {
         ctx.triggerToast('تنبيه أمني: لم يتم رصد أي ملف صورة رقمية صالحة للحقن.', 'warning');
         return;
     }
     
     if (!ctx.secretText.trim()) {
         ctx.triggerToast('تنبيه الحقل: الرجاء إدخال الرسالة السرية المراد تعميتها.', 'warning');
         return;
     }
     
     if (!ctx.password || !ctx.passValidation.valid) {
         ctx.triggerToast('خرق أمني: لا يمكن بدء التضمين بدون مفتاح تشفير مطابِق للسياسات المعقدة الصارمة.', 'error');
         return;
     }
     
     ctx.isLoading = true;
     ctx.loadingText = 'جاري توليد صفائف التشفير المتماثل AES-256 وحقن الخلايا الرقمية...';
     
     try {
         const formData = new FormData();
         formData.append('image', fileInput.files[0]);
         formData.append('text', ctx.secretText);
         formData.append('password', ctx.password);
         
         // حفظ الصورة الأصلية للمقارنة
         const originalFile = fileInput.files[0];
         ctx.originalImage = URL.createObjectURL(originalFile);
         
         const response = await fetch('/encode', { method: 'POST', body: formData });
         if (!response.ok) throw new Error(`استجابة الخادم غير مستقرة: ${response.status}`);
         
         const result = await response.json();
         
         if (result.status === 'error') {
             ctx.triggerToast(`الحماية تفشل: ${result.message}`, 'error');
             ctx.isLoading = false;
             return;
         }
         
         ctx.loadingText = 'تم دمج وتأمين البيانات! جاري توجيه حزمة التحميل الآمن...';
         ctx.triggerToast('تم تشفير النص وحقنه في الصورة بنجاح دون أثر ظاهري!', 'success');
         
         // حفظ مسار الصورة المخفية وعرض المقارنة
         ctx.stegoFilename = result.filename;
         ctx.stegoImage = '/uploads/' + result.filename;
         ctx.showComparison = true;
         ctx.isEmbedded = true;
         
     } catch (error) {
         console.error("[EMBED PROCESS ERROR]", error);
         ctx.triggerToast(`فشل بروتوكول التضمين: ${error.message}`, 'error');
     } finally {
         ctx.isLoading = false;
     }
 };
 
 // 4. دالة حفظ الصورة يدوياً
 window.saveStegoImageManually = function() {
     const ctx = getCyberContext();
     if (ctx && ctx.stegoFilename) {
         const downloadUrl = '/uploads/' + ctx.stegoFilename;
         const anchor = document.createElement('a');
         anchor.href = downloadUrl;
         anchor.download = ctx.stegoFilename;
         document.body.appendChild(anchor);
         anchor.click();
         anchor.remove();
         ctx.triggerToast('تم حفظ الصورة المخفية على جهازك', 'success');
     }
 };
 
 // 5. آلية تنفيذ فك التضمين واستخراج المخطوطات (Core Extraction Logic)
 window.runExtract = async function() {
     const ctx = getCyberContext();
     if (!ctx) return;
     
     const fileInput = document.querySelector('[x-ref="extractFile"]');
     if (!fileInput || !fileInput.files[0]) {
         ctx.triggerToast('طلب فك التشفير مرفوض: يرجى رفع ملف صورة الـ Stego أولاً.', 'warning');
         return;
     }
     
     if (!ctx.password) {
         ctx.triggerToast('مدخلات ناقصة: مفتاح فك التشفير ضروري لمطابقة مصفوفة الآمان.', 'warning');
         return;
     }
     
     ctx.isLoading = true;
     ctx.loadingText = 'جاري إخفاء البتات الدنيا (LSB) ومطابقة مفاتيح التفكيك الرقمي...';
     
     try {
         const formData = new FormData();
         formData.append('image', fileInput.files[0]);
         formData.append('password', ctx.password);
         
         const response = await fetch('/decode', { method: 'POST', body: formData });
         if (!response.ok) throw new Error(`خطأ في الوصول للبوابة الخلفية: ${response.status}`);
         
         const result = await response.json();
         
         if (result.status === 'error') {
             ctx.triggerToast(`فشل التعدين: ${result.message}`, 'error');
             ctx.isLoading = false;
             return;
         }
         
         if (result.status === 'success' && result.text) {
             ctx.triggerToast('✅ تم فك تشفير البيانات واستعادة المخطوطة العربية بنجاح آمن.', 'success');
             ctx.secretText = result.text;
             ctx.isExtracted = true;
         } else {
             ctx.triggerToast('مفتاح حظر البيانات غير صحيح، أو الصورة لا تحتوي على مصفوفة مشفرة.', 'error');
         }
     } catch (error) {
         console.error("[EXTRACT PROCESS ERROR]", error);
         ctx.triggerToast(`فشل نظام التفكيك الرقمي: ${error.message}`, 'error');
     } finally {
         ctx.isLoading = false;
     }
 };
 
 // 6. ربط أحداث الإدخال وعناصر التحكم تلقائياً دون تداخل
 document.addEventListener('DOMContentLoaded', () => {
     setTimeout(() => {
         const allButtons = Array.from(document.querySelectorAll('button'));
         
         const embedBtn = allButtons.find(btn => btn.textContent.includes('إخفاء النص') || btn.textContent.includes('تضمين'));
         if (embedBtn && !embedBtn.hasAttribute('data-cyber-bound')) {
             embedBtn.setAttribute('data-cyber-bound', 'true');
             embedBtn.removeAttribute('onclick');
             embedBtn.addEventListener('click', (e) => {
                 e.preventDefault();
                 window.runEmbed();
             });
         }
         
         const extractBtn = allButtons.find(btn => btn.textContent.includes('استخراج') || btn.textContent.includes('تفكيك'));
         if (extractBtn && !extractBtn.hasAttribute('data-cyber-bound')) {
             extractBtn.setAttribute('data-cyber-bound', 'true');
             extractBtn.removeAttribute('onclick');
             extractBtn.addEventListener('click', (e) => {
                 e.preventDefault();
                 window.runExtract();
             });
         }
         
         const saveBtn = allButtons.find(btn => btn.textContent.includes('تحميل وحفظ'));
         if (saveBtn && !saveBtn.hasAttribute('data-cyber-bound')) {
             saveBtn.setAttribute('data-cyber-bound', 'true');
             saveBtn.addEventListener('click', (e) => {
                 e.preventDefault();
                 window.saveStegoImageManually();
             });
         }
     }, 600);
 });