document.addEventListener('DOMContentLoaded', function () {

    // --- 【修改點 1】重新定義我們要操作的 DOM 元素 ---
    const predictBtn = document.getElementById('predict-btn');
    const statusContainer = document.getElementById('status-container'); // 狀態的總容器
    const performanceWrapper = document.getElementById('performance-section-wrapper'); // 模型表現的容器
    const progressIndicator = document.getElementById('progress-indicator'); // 進度指示器 (轉圈+文字)
    const statusText = document.getElementById('status-text'); // 狀態文字
    const resultSection = document.getElementById('result-section'); // 最終結果區
    const resultText = document.getElementById('result-text');
    const totalPriceText = document.getElementById('total-price-text');

    // resultsPanel 變數已移除，因為它不存在且多餘

    let streamHandled; // 標誌：用於判斷是否已處理來自伺服器的最終消息

    predictBtn.addEventListener('click', function () {
        const address = document.getElementById('address-input').value;
        if (!address) {
            alert('請務必輸入地址！');
            return;
        }

        streamHandled = false; // 每次點擊時重置標誌

        const userFeatures = {
            '建物總坪數': document.getElementById('ping-input').value,
            '最終_屋齡': document.getElementById('age-input').value,
            '建物型態_分類': document.getElementById('building-type-input').value,
            '最終_主要建材': document.getElementById('material-input').value,
            '最終_總樓層數': document.getElementById('total-floor-input').value,
            '最終_移轉樓層': document.getElementById('current-floor-input').value,
            '建物現況格局_房': document.getElementById('layout-room-input').value,
            '建物現況格局_廳': document.getElementById('layout-living-input').value,
            '建物現況格局_衛': document.getElementById('layout-bath-input').value,
            '最終_車位類別': document.getElementById('parking-type-input').value
        };

        const filledFeatures = {};
        for (const key in userFeatures) {
            if (userFeatures[key] !== null && userFeatures[key] !== '') {
                filledFeatures[key] = userFeatures[key];
            }
        }

        const requestBody = {
            address: address,
            features: filledFeatures
        };

        // --- 【修改點 2】更新 UI 的操作邏輯 ---
        predictBtn.disabled = true;
        predictBtn.textContent = '預測中...';

        // 隱藏模型表現和最終結果
        performanceWrapper.classList.add('hidden');
        resultSection.classList.add('hidden');

        // 顯示進度指示器
        statusContainer.classList.remove('hidden'); // 確保狀態總容器是可見的
        progressIndicator.classList.remove('hidden');
        statusText.textContent = '正在初始化...';

        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => {
                        throw new Error(errData.error || `伺服器錯誤 (HTTP ${response.status})`);
                    }).catch(() => {
                        throw new Error(`伺服器錯誤 (HTTP ${response.status})`);
                    });
                }
                if (!response.body) {
                    throw new Error("伺服器響應格式不支援流式讀取。");
                }
                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                function processStream() {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            if (!streamHandled && resultSection.classList.contains('hidden')) {
                                handleStreamData({ error: "從伺服器接收數據時連接意外中斷。" });
                            }
                            return;
                        }

                        const chunk = decoder.decode(value, { stream: true });
                        const lines = chunk.split('\n\n');
                        lines.forEach(line => {
                            if (line.startsWith('data:')) {
                                const jsonData = line.substring(5).trim();
                                if (jsonData) {
                                    try {
                                        const data = JSON.parse(jsonData);
                                        handleStreamData(data);
                                    } catch (e) {
                                        console.error("解析JSON失敗:", jsonData, e);
                                        handleStreamData({ error: `解析伺服器數據出錯: ${e.message}` });
                                    }
                                }
                            }
                        });
                        processStream();
                    }).catch(streamReadError => {
                        console.error("讀取流時發生錯誤:", streamReadError);
                        handleStreamData({ error: `讀取伺服器響應流時出錯: ${streamReadError.message}` });
                    });
                }
                processStream();
            })
            .catch(error => {
                console.error("請求或處理過程中發生錯誤:", error);
                handleStreamData({ error: `${error.message}` });
            });
    });

    function handleStreamData(data) {
        if (data.error) {
            // --- 【修改點 3】更新錯誤處理的 UI 邏輯 ---
            progressIndicator.classList.remove('hidden'); // 確保進度區可見
            statusText.textContent = `錯誤：${data.error}`; // 在進度區顯示錯誤
            resultSection.classList.add('hidden'); // 隱藏結果區

            predictBtn.disabled = false;
            predictBtn.textContent = '🚀 開始預測';
            streamHandled = true;
        } else {
            if (data.status) {
                statusText.textContent = data.status;
            }

            if (data.prediction) {
                // --- 【修改點 4】更新成功時的 UI 邏輯 ---
                progressIndicator.classList.add('hidden'); // 隱藏進度指示器
                resultSection.classList.remove('hidden'); // 顯示最終結果區

                resultText.textContent = data.prediction;

                if (data.total_price && data.total_price !== "N/A" && data.total_price.trim() !== "") {
                    totalPriceText.textContent = `(預估總價約：${data.total_price})`;
                    totalPriceText.style.display = 'block';
                } else {
                    totalPriceText.style.display = 'none';
                }

                predictBtn.disabled = false;
                predictBtn.textContent = '🚀 開始預測';
                streamHandled = true;
            }
        }
    }
});