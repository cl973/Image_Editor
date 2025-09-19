Page({
  /**
   * 页面的初始数据
   */
  data: {
    sliderValue1: 50, // 泛黄
    sliderValue2: 50, // 褪色
    sliderValue3: 50, // 划痕
    sliderValue4: 50  // 高斯模糊（保持原有参数名）
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {},

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {},

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {},

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {},

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {},

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {
    // 停止下拉刷新动画
    wx.stopPullDownRefresh();
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {},

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {},

  // 泛黄输入框变化处理
  onInputChange1(e) {
    let input1 = e.detail.value;
    // 转换为数字，非数字则取当前值，限制范围0-100
    input1 = isNaN(Number(input1)) ? this.data.sliderValue1 : Number(input1);
    input1 = Math.max(0, Math.min(100, input1));
    this.setData({ sliderValue1: input1 });
  },

  // 泛黄滑块变化处理
  onSliderChange1(e) {
    this.setData({ sliderValue1: e.detail.value });
  },

  // 褪色输入框变化处理
  onInputChange2(e) {
    let input2 = e.detail.value;
    input2 = isNaN(Number(input2)) ? this.data.sliderValue2 : Number(input2);
    input2 = Math.max(0, Math.min(100, input2));
    this.setData({ sliderValue2: input2 });
  },

  // 褪色滑块变化处理
  onSliderChange2(e) {
    this.setData({ sliderValue2: e.detail.value });
  },

  // 划痕输入框变化处理
  onInputChange3(e) {
    let input3 = e.detail.value;
    input3 = isNaN(Number(input3)) ? this.data.sliderValue3 : Number(input3);
    input3 = Math.max(0, Math.min(100, input3));
    this.setData({ sliderValue3: input3 });
  },

  // 划痕滑块变化处理
  onSliderChange3(e) {
    this.setData({ sliderValue3: e.detail.value });
  },

  // 高斯模糊输入框变化处理（保持原有逻辑）
  onInputChange4(e) {
    let input4 = e.detail.value;
    input4 = isNaN(Number(input4)) ? this.data.sliderValue4 : Number(input4);
    input4 = Math.max(0, Math.min(100, input4));
    this.setData({ sliderValue4: input4 });
  },

  // 高斯模糊滑块变化处理（保持原有逻辑）
  onSliderChange4(e) {
    this.setData({ sliderValue4: e.detail.value });
  },

  // 返回编辑页面（修复跳转方式）
  backeditor() {
    // 返回上一页（兼容非tabBar页面）
    wx.switchTab({
      url: '/pages/editor1/editor1',
    })
  },

  // 上传参数并处理图片
  uploadparams() {
    // 获取全局实例和图片数据
    const app = getApp();
    const originalImages = app.globalData.originalImages || [];
    // const { sliderValue1, sliderValue2, sliderValue3, sliderValue4 } = this.data;
    const that = this;

    // 校验图片是否存在
    if (!originalImages.length) {
      wx.showToast({
        title: '请先选择图片',
        icon: 'none',
        duration: 2000
      });
      return;
    }

    const type = 'xtpzj';
    wx.showLoading({
      title: `上传中（共${originalImages.length}张）...`,
      mask: true
    });
    console.log("参数1",that.data.sliderValue1)
    console.log("参数1",that.data.sliderValue2)
    console.log("参数1",that.data.sliderValue3)
    console.log("参数1",that.data.sliderValue4)
    // 单个图片上传函数
    const uploadWithParams = (filePath, index) => {
      return new Promise((resolve, reject) => {
        wx.uploadFile({
          url: "http://1.15.143.65:8000/image-process",
          filePath: filePath,
          name: 'image',
          // header: { 'content-type': 'multipart/form-data' },
          formData: {  // 此处无需修改，参数名与服务器约定一致即可
            'type': type,
            'fanhuang': that.data.sliderValue1,  // 强制转为数字
            'tuise': that.data.sliderValue2,
            'huahen': that.data.sliderValue3,
            'gaosimohu': that.data.sliderValue4
          },
          success: (res) => {
            try {
              console.log("chenggong1")
              const result = JSON.parse(res.data);
              // 关键修改1：匹配服务器返回的字段名 `image_url`（下划线），而非 `imageUrl`
              if (result.success && result.image_url) {
                // 关键修改2：将服务器返回的 `image_url` 赋值给 `url`，后续逻辑不变
                resolve({ url: result.image_url });
                console.log("chenggong2")
              } else {
                // 若服务器失败时返回的是其他字段（如 `error`），需改为 `result.error`，此处按原逻辑保留 `msg`
                console.log("shibai");
                console.log(result.image_url)
                reject(`第${index+1}张：${result.msg || '处理异常'}`);
              }
            } catch (e) {
              reject(`第${index+1}张：服务器返回格式错误`);
            }
          },
          fail: (err) => {
            console.error('上传失败详情:', err);
            reject(`第${index+1}张：${err.errMsg}`);
          }
        });
      });
    };
  
    // 批量上传所有图片（无需修改）
    const uploadPromises = originalImages.map((filePath, index) => 
      uploadWithParams(filePath, index)
    );
  
    // 处理上传结果（无需修改）
    Promise.allSettled(uploadPromises)
      .then(results => {
        let processingUrls = [];
        let successCount = 0;
        let errorMsg = '';
  
        results.forEach(result => {
          if (result.status === 'fulfilled') {
            // 此处 `result.value.url` 对应上面 `resolve({ url: ... })` 中的 `url`，逻辑一致，无需修改
            processingUrls.push(result.value.url);
            successCount++;
          } else {
            errorMsg += result.reason + '; ';
          }
        });
  
        // 更新全局处理后图片数组（无需修改）
        getApp().globalData.processedImages = processingUrls;
  
        // 显示结果提示（无需修改）
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
        // 跳转到展示页（无需修改）
        wx.switchTab({ url: '/pages/showpic/showpic' });
      });
  }
});
