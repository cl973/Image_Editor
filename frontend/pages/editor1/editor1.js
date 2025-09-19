Page({
  data: {
    previewUrls: [],
    tip: '',
    meteorLefts: [],
    meteorDelays: [] ,
    bg:"bg.png"
  },
  onShow() {
    // 从全局数据获取已选择的图片（关键：确保数据来源正确）
    const app = getApp();
    console.log("全局originalImages数组（所有路径）：", app.globalData.originalImages);
    this.setData({
      previewUrls: app.globalData.originalImages || [] // 假设全局数据存在这里
    });
    console.log("全局originalImages数组（所有路径1）：", app.globalData.originalImages);

    // 流星相关逻辑（不变）
    const lefts = [];
    const delays = [];
    for (let i = 0; i < 50; i++) {
      lefts.push(Math.random() * 100+50);
      delays.push(Math.random() * 3);
    }
    this.setData({ meteorLefts: lefts, meteorDelays: delays });
  },


  ImageDenoising() {
    this.setData({ previewUrls: getApp().globalData.originalImages });
    wx.navigateTo({
      url: '/pages/ltpfx/ltpfx',
    });
  },
  ImageEnhancement() {
    this.setData({ previewUrls: getApp().globalData.originalImages });
    this.processImage2();
  },
  processImage2() {
    const that = this;
    const { previewUrls } = this.data;
    if (!previewUrls || previewUrls.length === 0) {
      this.setData({ tip: '请先选择照片' });
      return;
    }
    this.setData({ tip: `正在处理 ${previewUrls.length} 张图片...`, processedUrls: [] });
    const originalImages = getApp().globalData.originalImages || [];
    if (!originalImages.length) {
      wx.showToast({ title: '请先选择图片（全局数组为空）', icon: 'none', duration: 2000 });
      return;
    }
    const type = 'ltpfx';
    wx.showLoading({ title: `上传中（共${originalImages.length}张）...`, mask: true });
    const uploadWithParams = (filePath, index) => {
      return new Promise((resolve, reject) => {
        wx.uploadFile({
          url: "http://1.15.143.65:8000/image-process",
          filePath: filePath,
          name: 'image',
          // header: { 'content-type': 'multipart/form-data' },
          formData: { 'type': type },
          success: (res) => {
            try {
              const result = JSON.parse(res.data);
              // 关键修改：将 result.imageUrl 改为 result.image_url（匹配服务器返回的字段名）
              if (result.success && result.image_url) {
                resolve({ url: result.image_url }); // 同样使用 image_url 传递图片地址
              } else {
                reject(`第${index+1}张：${result.msg || '处理异常'}`);
              }
            } catch (e) {
              reject(`第${index+1}张：服务器返回格式错误`);
            }
          },
          fail: (err) => {
            reject(`第${index+1}张：${err.errMsg}`);
          }
        });
      });
    };
    
    const uploadPromises = originalImages.map((filePath, index) => uploadWithParams(filePath, index));
    
    Promise.allSettled(uploadPromises)
      .then(results => {
        let processingUrls = [];
        let successCount = 0;
        let errorMsg = '';
        results.forEach(result => {
          if (result.status === 'fulfilled') {
            processingUrls.push(result.value.url); // 这里的 url 对应上面 resolve 传递的 url，无需修改
            successCount++;
          } else {
            errorMsg += result.reason + '; ';
          }
        });
        getApp().globalData.processedImages = processingUrls;
        if (successCount > 0) {
          wx.showToast({
            title: `成功${successCount}/${originalImages.length}张`,
            icon: 'success',
            duration: 2000
          });
        } else {
          wx.showToast({
            title: `全部失败：${errorMsg.slice(0, -2)}`,
            icon: 'none',
            duration: 3000
          });
        }
      })
      .finally(() => {
        wx.hideLoading();
        wx.switchTab({ url: '/pages/showpic/showpic' });
      });
  },
  onHide() {},
  onUnload() {},
  onPullDownRefresh() {},
  onReachBottom() {},
  onShareAppMessage() {}
});