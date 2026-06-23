(function () {
    let currentXhr = null;
    let evalInterval = null;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        // محاولة الربط عن طريق الـ ID أولاً كخيار آمن، أو عبر النص كخيار احتياطي
        const experimentBtn = document.getElementById('runExperimentBtn') || findButtonByText('تشغيل التجربة');
        if (experimentBtn) {
            experimentBtn.addEventListener('click', runExperiment);
        }

        const startEvalBtn = document.getElementById('startEvalBtn');
        if (startEvalBtn) {
            startEvalBtn.addEventListener('click', runBaselineComparison);
        }

        const imageInput = document.getElementById('adminImageInput');
        if (imageInput) {
            imageInput.addEventListener('change', handleImagePreview);
        }
    }

    function findButtonByText(text) {
        const buttons = document.querySelectorAll('button');
        for (let btn of buttons) {
            if (btn.innerText && btn.innerText.includes(text)) {
                return btn;
            }
        }
        return null;
    }

    function handleImagePreview(e) {
        const file = e.target.files[0];
        const placeholder = document.getElementById('uploadPlaceholder');

        if (file) {
            const reader = new FileReader();
            reader.onload = function (ev) {
                if (placeholder) {
                    placeholder.style.display = 'none';
                }

                let previewImg = document.getElementById('adminImagePreview');

                if (!previewImg) {
                    previewImg = document.createElement('img');
                    previewImg.id = 'adminImagePreview';
                    previewImg.className = "w-full h-full max-h-[190px] rounded-2xl border border-blue-500/40 shadow-xl glow-blue block object-contain transition-all duration-300 transform hover:scale-[1.01]";
                    e.target.parentNode.appendChild(previewImg);
                }

                previewImg.src = ev.target.result;
            };
            reader.readAsDataURL(file);
        } else {
            if (placeholder) {
                placeholder.style.display = 'block';
            }
            const previewImg = document.getElementById('adminImagePreview');
            if (previewImg) previewImg.remove();
        }
    }

    window.cancelProcessing = function () {
        fetch('/admin/cancel_evaluation', { method: 'POST' })
            .catch(err => console.log("تم إرسال إشارة الإلغاء للسيرفر"));

        if (currentXhr) {
            currentXhr.abort();
            currentXhr = null;
        }
        if (evalInterval) {
            clearInterval(evalInterval);
            evalInterval = null;
        }
        window.dispatchEvent(new CustomEvent('update-progress', { detail: 0 }));
        alert('⚠️ تم إلغاء معالجة الطلب بنجاح .');
    };

    async function runExperiment(e) {
        e.preventDefault();

        const imageInput = document.getElementById('adminImageInput');
        const imageFile = imageInput ? imageInput.files[0] : null;
        const textarea = document.querySelector('textarea');
        const arabicText = textarea ? textarea.value : '';

        if (!imageFile) {
            alert('⚠️ الرجاء اختيار صورة أولاً قبل تشغيل التجربة.');
            return;
        }

        if (!arabicText.trim()) {
            alert('⚠️ الرجاء إدخال النص العربي المراد إخفاءه.');
            return;
        }

        const expResultCard = document.getElementById('expResultCard');
        if (expResultCard) expResultCard.style.display = 'none';

        window.dispatchEvent(new CustomEvent('update-progress', { detail: 0 }));
        window.dispatchEvent(new CustomEvent('update-status', { detail: 'loading_exp' }));

        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('text', arabicText);

        const xhr = new XMLHttpRequest();
        currentXhr = xhr;

        xhr.upload.addEventListener('progress', function (event) {
            if (event.lengthComputable) {
                const percentComplete = Math.round((event.loaded / event.total) * 85);
                window.dispatchEvent(new CustomEvent('update-progress', { detail: percentComplete }));
            }
        });

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 3) {
                window.dispatchEvent(new CustomEvent('update-progress', { detail: 95 }));
            }
            if (xhr.readyState === 4) {
                currentXhr = null;
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const result = JSON.parse(xhr.responseText);
                        window.dispatchEvent(new CustomEvent('update-progress', { detail: 100 }));

                        const expResultTbody = document.querySelector('#expResultTable tbody');

                        if (expResultCard && expResultTbody) {
                            // تأمين قراءة المتغيرات الأساسية من الـ Backend
                            const psnrSas = result.psnr ?? result.psnr_sas;
                            const ssimSas = result.ssim ?? result.ssim_sas;
                            const berSas = result.ber ?? result.ber_sas;

                            // بناء الجدول مع فحص صارم للقيم الصفرية وتحديد اتجاه النص للأرقام LTR
                            expResultTbody.innerHTML = `
                              <tr class="hover:bg-blue-500/5 transition-all">
                                  <td class="text-right font-bold text-blue-600 dark:text-blue-400">التضمين الأساسي المقترح (SAS)</td>
                                  <td dir="ltr">${(psnrSas !== undefined && psnrSas !== null) ? parseFloat(psnrSas).toFixed(2) + ' dB' : '-'}</td>
                                  <td dir="ltr">${(ssimSas !== undefined && ssimSas !== null) ? parseFloat(ssimSas).toFixed(4) : '-'}</td>
                                  <td dir="ltr">${(berSas !== undefined && berSas !== null) ? parseFloat(berSas).toFixed(4) : '-'}</td>
                              </tr>
                              <tr class="hover:bg-amber-500/5 transition-all">
                                  <td class="text-right font-bold text-amber-600 dark:text-amber-400">هجوم ضغط الصور (JPEG Attack)</td>
                                  <td dir="ltr">${(result.psnr_jpeg !== undefined && result.psnr_jpeg !== null) ? parseFloat(result.psnr_jpeg).toFixed(2) + ' dB' : '-'}</td>
                                  <td dir="ltr">${(result.ssim_jpeg !== undefined && result.ssim_jpeg !== null) ? parseFloat(result.ssim_jpeg).toFixed(4) : '-'}</td>
                                  <td dir="ltr">${(result.ber_jpeg !== undefined && result.ber_jpeg !== null) ? parseFloat(result.ber_jpeg).toFixed(4) : '-'}</td>
                              </tr>
                              <tr class="hover:bg-purple-500/5 transition-all">
                                  <td class="text-right font-bold text-purple-600 dark:text-purple-400">هجوم حقن الضوضاء (Gaussian Noise)</td>
                                  <td dir="ltr">${(result.psnr_noise !== undefined && result.psnr_noise !== null) ? parseFloat(result.psnr_noise).toFixed(2) + ' dB' : '-'}</td>
                                  <td dir="ltr">${(result.ssim_noise !== undefined && result.ssim_noise !== null) ? parseFloat(result.ssim_noise).toFixed(4) : '-'}</td>
                                  <td dir="ltr">${(result.ber_noise !== undefined && result.ber_noise !== null) ? parseFloat(result.ber_noise).toFixed(4) : '-'}</td>
                              </tr>
                              <tr class="hover:bg-red-500/5 transition-all">
                                  <td class="text-right font-bold text-red-600 dark:text-red-400">هجوم قص أطراف الصورة (Cropping Attack)</td>
                                  <td dir="ltr">${(result.psnr_crop !== undefined && result.psnr_crop !== null) ? parseFloat(result.psnr_crop).toFixed(2) + ' dB' : '-'}</td>
                                  <td dir="ltr">${(result.ssim_crop !== undefined && result.ssim_crop !== null) ? parseFloat(result.ssim_crop).toFixed(4) : '-'}</td>
                                  <td dir="ltr">${(result.ber_crop !== undefined && result.ber_crop !== null) ? parseFloat(result.ber_crop).toFixed(4) : '-'}</td>
                              </tr>
                          `;

                            expResultCard.style.display = 'block';
                            expResultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        }

                        setTimeout(() => {
                            window.dispatchEvent(new CustomEvent('update-status', { detail: 'idle' }));
                            alert('✨ تمت التجربة بنجاح.');
                        }, 300);

                    } catch (parseErr) {
                        window.dispatchEvent(new CustomEvent('update-status', { detail: 'idle' }));
                        alert('❌ حدث خطأ أثناء فك حزم بيانات السيرفر .');
                    }
                } else if (xhr.status !== 0) {
                    window.dispatchEvent(new CustomEvent('update-status', { detail: 'idle' }));
                    alert('❌ حدث خطأ أثناء معالجة التجربة: ' + xhr.statusText);
                }
            }
        };

        xhr.open('POST', '/admin/admin_encode', true);
        xhr.send(formData);
    }

    async function runBaselineComparison() {

        window.dispatchEvent(
            new CustomEvent('update-progress', {
                detail: 0
            })
        );

        window.dispatchEvent(
            new CustomEvent('update-status', {
                detail: 'loading_eval'
            })
        );

        // بدء المهمة
        await fetch('/admin/baseline_comparison', {
            method: 'POST'
        });

        // مراقبة التقدم
        evalInterval = setInterval(async () => {

            const response =
                await fetch('/admin/evaluation_progress');

            const progress =
                await response.json();

            window.dispatchEvent(
                new CustomEvent(
                    'update-progress',
                    {
                        detail: progress.progress
                    }
                )
            );

            // إذا انتهى السيرفر
            if (progress.finished) {

                clearInterval(evalInterval);

                loadEvaluationResults();

            }

        }, 80);

    }

    async function loadEvaluationResults() {

        const response =
            await fetch('/admin/evaluation_results');

        const data =
            await response.json();

        window.dispatchEvent(
            new CustomEvent(
                'update-progress',
                {
                    detail: 100
                }
            )
        );

        window.dispatchEvent(
            new CustomEvent(
                'update-status',
                {
                    detail: 'finished'
                }
            )
        );

        let evalSum = {
            psnr_sas: 0,
            ssim_sas: 0,
            ber_sas: 0,
            psnr_lsb: 0,
            ssim_lsb: 0,
            ber_lsb: 0,
            chi_sas: 0,
            rs_sas: 0,
            entropy_sas: 0,
            chi_lsb: 0,
            rs_lsb: 0,
            entropy_lsb: 0
        };

        let attackSum = {
            psnr_jpeg: 0,
            ssim_jpeg: 0,
            ber_jpeg: 0,
            psnr_noise: 0,
            ssim_noise: 0,
            ber_noise: 0,
            psnr_crop: 0,
            ssim_crop: 0,
            ber_crop: 0
        };

        let imgCount = data.images ? data.images.length : 0;

        const evalTbody = document.querySelector('#evalTable tbody');

        if (evalTbody && data.images) {

            evalTbody.innerHTML = '';

            data.images.forEach(img => {

                const row = evalTbody.insertRow();

                row.insertCell(0).innerHTML =
                    `<img src="/dataset/${img.image}"
        width="50"
        height="50"
        style="border-radius:8px;display:inline-block;margin-bottom:4px;">
        <br>
        <span class="text-xs">${img.image}</span>`;

                row.insertCell(1).innerHTML =
                    `<span dir="ltr">${img.psnr_sas.toFixed(2)}</span>`;

                row.insertCell(2).innerHTML =
                    `<span dir="ltr">${img.ssim_sas.toFixed(4)}</span>`;

                row.insertCell(3).innerHTML =
                    `<span dir="ltr">${img.ber_sas.toFixed(4)}</span>`;

                row.insertCell(4).innerHTML =
                    `<span dir="ltr">${img.psnr_lsb.toFixed(2)}</span>`;

                row.insertCell(5).innerHTML =
                    `<span dir="ltr">${img.ssim_lsb.toFixed(4)}</span>`;

                row.insertCell(6).innerHTML =
                    `<span dir="ltr">${img.ber_lsb.toFixed(4)}</span>`;

                row.insertCell(7).innerHTML =
                    `<span dir="ltr">${img.chi_sas.toFixed(2)}</span>`;

                row.insertCell(8).innerHTML =
                    `<span dir="ltr">${img.rs_sas.toFixed(3)}</span>`;

                row.insertCell(9).innerHTML =
                    `<span dir="ltr">${img.entropy_sas.toFixed(3)}</span>`;

                row.insertCell(10).innerHTML =
                    `<span dir="ltr">${img.chi_lsb.toFixed(2)}</span>`;

                row.insertCell(11).innerHTML =
                    `<span dir="ltr">${img.rs_lsb.toFixed(3)}</span>`;

                row.insertCell(12).innerHTML =
                    `<span dir="ltr">${img.entropy_lsb.toFixed(3)}</span>`;

                // جمع المتوسطات
                evalSum.psnr_sas += img.psnr_sas || 0;
                evalSum.ssim_sas += img.ssim_sas || 0;
                evalSum.ber_sas += img.ber_sas || 0;

                evalSum.psnr_lsb += img.psnr_lsb || 0;
                evalSum.ssim_lsb += img.ssim_lsb || 0;
                evalSum.ber_lsb += img.ber_lsb || 0;

                evalSum.chi_sas += img.chi_sas || 0;
                evalSum.rs_sas += img.rs_sas || 0;
                evalSum.entropy_sas += img.entropy_sas || 0;

                evalSum.chi_lsb += img.chi_lsb || 0;
                evalSum.rs_lsb += img.rs_lsb || 0;
                evalSum.entropy_lsb += img.entropy_lsb || 0;

            });

            const evalCells =
                document.querySelectorAll('#evalTable tfoot tr td');

            if (evalCells.length > 1 && imgCount > 0) {

                evalCells[1].innerHTML =
                    `<span dir="ltr">${(evalSum.psnr_sas / imgCount).toFixed(2)}</span>`;

                evalCells[2].innerHTML =
                    `<span dir="ltr">${(evalSum.ssim_sas / imgCount).toFixed(4)}</span>`;

                evalCells[3].innerHTML =
                    `<span dir="ltr">${(evalSum.ber_sas / imgCount).toFixed(4)}</span>`;

                evalCells[4].innerHTML =
                    `<span dir="ltr">${(evalSum.psnr_lsb / imgCount).toFixed(2)}</span>`;

                evalCells[5].innerHTML =
                    `<span dir="ltr">${(evalSum.ssim_lsb / imgCount).toFixed(4)}</span>`;

                evalCells[6].innerHTML =
                    `<span dir="ltr">${(evalSum.ber_lsb / imgCount).toFixed(4)}</span>`;

                evalCells[7].innerHTML =
                    `<span dir="ltr">${(evalSum.chi_sas / imgCount).toFixed(2)}</span>`;

                evalCells[8].innerHTML =
                    `<span dir="ltr">${(evalSum.rs_sas / imgCount).toFixed(3)}</span>`;

                evalCells[9].innerHTML =
                    `<span dir="ltr">${(evalSum.entropy_sas / imgCount).toFixed(3)}</span>`;

                evalCells[10].innerHTML =
                    `<span dir="ltr">${(evalSum.chi_lsb / imgCount).toFixed(2)}</span>`;

                evalCells[11].innerHTML =
                    `<span dir="ltr">${(evalSum.rs_lsb / imgCount).toFixed(3)}</span>`;

                evalCells[12].innerHTML =
                    `<span dir="ltr">${(evalSum.entropy_lsb / imgCount).toFixed(3)}</span>`;
            }
            const attackTbody = document.querySelector('#attackTable tbody');

            if (attackTbody && data.images) {

                attackTbody.innerHTML = '';

                data.images.forEach(img => {

                    const row = attackTbody.insertRow();

                    row.insertCell(0).innerHTML =
                        `<img src="/dataset/${img.image}"
        width="50"
        height="50"
        style="border-radius:8px;display:inline-block;margin-bottom:4px;">
        <br>
        <span class="text-xs">${img.image}</span>`;

                    row.insertCell(1).innerHTML = `<span dir="ltr">${img.psnr_jpeg.toFixed(2)}</span>`;
                    row.insertCell(2).innerHTML = `<span dir="ltr">${img.ssim_jpeg.toFixed(4)}</span>`;
                    row.insertCell(3).innerHTML = `<span dir="ltr">${img.ber_jpeg.toFixed(4)}</span>`;

                    row.insertCell(4).innerHTML = `<span dir="ltr">${img.psnr_noise.toFixed(2)}</span>`;
                    row.insertCell(5).innerHTML = `<span dir="ltr">${img.ssim_noise.toFixed(4)}</span>`;
                    row.insertCell(6).innerHTML = `<span dir="ltr">${img.ber_noise.toFixed(4)}</span>`;

                    row.insertCell(7).innerHTML = `<span dir="ltr">${img.psnr_crop.toFixed(2)}</span>`;
                    row.insertCell(8).innerHTML = `<span dir="ltr">${img.ssim_crop.toFixed(4)}</span>`;
                    row.insertCell(9).innerHTML = `<span dir="ltr">${img.ber_crop.toFixed(4)}</span>`;

                    attackSum.psnr_jpeg += img.psnr_jpeg || 0;
                    attackSum.ssim_jpeg += img.ssim_jpeg || 0;
                    attackSum.ber_jpeg += img.ber_jpeg || 0;

                    attackSum.psnr_noise += img.psnr_noise || 0;
                    attackSum.ssim_noise += img.ssim_noise || 0;
                    attackSum.ber_noise += img.ber_noise || 0;

                    attackSum.psnr_crop += img.psnr_crop || 0;
                    attackSum.ssim_crop += img.ssim_crop || 0;
                    attackSum.ber_crop += img.ber_crop || 0;

                });

                const attackCells =
                    document.querySelectorAll('#attackTable tfoot tr td');

                if (attackCells.length > 1 && imgCount > 0) {

                    attackCells[1].innerHTML = `<span dir="ltr">${(attackSum.psnr_jpeg / imgCount).toFixed(2)}</span>`;
                    attackCells[2].innerHTML = `<span dir="ltr">${(attackSum.ssim_jpeg / imgCount).toFixed(4)}</span>`;
                    attackCells[3].innerHTML = `<span dir="ltr">${(attackSum.ber_jpeg / imgCount).toFixed(4)}</span>`;

                    attackCells[4].innerHTML = `<span dir="ltr">${(attackSum.psnr_noise / imgCount).toFixed(2)}</span>`;
                    attackCells[5].innerHTML = `<span dir="ltr">${(attackSum.ssim_noise / imgCount).toFixed(4)}</span>`;
                    attackCells[6].innerHTML = `<span dir="ltr">${(attackSum.ber_noise / imgCount).toFixed(4)}</span>`;

                    attackCells[7].innerHTML = `<span dir="ltr">${(attackSum.psnr_crop / imgCount).toFixed(2)}</span>`;
                    attackCells[8].innerHTML = `<span dir="ltr">${(attackSum.ssim_crop / imgCount).toFixed(4)}</span>`;
                    attackCells[9].innerHTML = `<span dir="ltr">${(attackSum.ber_crop / imgCount).toFixed(4)}</span>`;
                }
            }

            window.dispatchEvent(
                new CustomEvent('update-status', {
                    detail: 'finished'
                })
            );

            window.dispatchEvent(
                new CustomEvent('update-progress', {
                    detail: 100
                })
            );

        }

        alert("✅ اكتمل التقييم بنجاح");

    }

})();
