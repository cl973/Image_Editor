// pages/ltpfx/ltpfx.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    sliderValue1:50,
    sliderValue2:50,
    sliderValue3:50,
    sliderValue4:50,
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  },

  onInputChange1(e){
    const input1=e.detail.value;
    input1=Number(input1)||0;
    this.setData({
      sliderValue1:input1
    })
  },
  onSliderChange1(e) {
    const value1 = e.detail.value;
    let value=Number(value1)||0;
    this.setData({
      sliderValue1:value
    })
  },
  onInputChange2(e){
    const input2=e.detail.value;
    input2=Number(input2)||0;
    this.setData({
      sliderValue2:input2
    })
  },

  onSliderChange2(e) {
    const value2 = e.detail.value;
    let value=Number(value2)||0;
    this.setData({
      sliderValue2:value
    })
  },

  onInputChange3(e){
    const input3=e.detail.value;
    input3=Number(input3)||this.data.sliderValue3;
    this.setData({
      sliderValue3:input3
    })
  },
  onSliderChange3(e) {
    const value3 = e.detail.value;
    let value=Number(value3)||0;
    this.setData({
      sliderValue3:value
    })
  },
  onInputChange4(e){
    const input4=e.detail.value;
    input4=Number(input4)||this.data.sliderValue4;
    this.setData({
      sliderValue4:input4
    })
  },
  onSliderChange4(e) {
    const value4 = e.detail.value;
    let value=Number(value4)||0;
    this.setData({
      sliderValue4:value
    })
  },
  backeditor(){
    wx.switchTab({  
      url: '/pages/editor1/editor1'
    })
  },



  uploadparams() {
    // 1. 获取全局数据中的图片数组（核心修改：从全局取图，而非单个imagePath）
    const app = getApp(); // 获取小程序全局实例
    const originalImages = app.globalData.originalImages || []; // 全局图片数组
    const { sliderValue1, sliderValue2, sliderValue3, sliderValue4 } = this.data;
    const that = this;
  
    // 2. 校验：全局图片数组是否有内容（替代原单个imagePath的校验）
    if (!originalImages.length) {
      wx.showToast({
        title: '请先选择图片（全局数组为空）',
        icon: 'none',
        duration: 2000
      });
      return;
    }
  

    const type = 'xtpzj'; // 示例：假设type值为'xtpzj'，可根据后端需求修改
  
    wx.showLoading({
      title: `上传中（共${originalImages.length}张）...`,
      mask: true
    });
  
    // 4. 单个图片上传函数（逻辑不变，仅参数适配全局数组）
    const uploadWithParams = (filePath, index) => {
      return new Promise((resolve, reject) => {
        wx.uploadFile({
          url: "http://1.15.143.65:8000/image-process", // 端口不变
          filePath: filePath, // 数组中单个图片的路径
          name: 'image', // 服务器接收图片的固定参数名
          header: {
            'content-type': 'multipart/form-data'
          },
          formData: {  // 携带四个参数 + type + 图片索引（方便后端区分图片）
            'type': type, // 已修复：使用定义好的type值
            'fanhuang': sliderValue1,  // 泛黄
            'tuise': sliderValue2,     // 褪色
            'huahen': sliderValue3,    // 划痕
            'gaosimohu': sliderValue4, // 高斯噪声
            'imageIndex': index // 可选：传递图片在数组中的索引，后端可按顺序处理
          },
          success: (res) => {
            try {
              const result = JSON.parse(res.data);
              if (result.success && result.imageUrl) {
                resolve({
                   // 保留索引，确保结果与原数组顺序一致
                  url: result.imageUrl,
                  
                });
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
  
    // 5. 核心修改：批量处理全局图片数组（生成所有图片的上传Promise）
    const uploadPromises = originalImages.map((filePath, index) => {
      return uploadWithParams(filePath, index); // 给每张图加索引，保证顺序
    });
  
   
    Promise.allSettled(uploadPromises)
      .then(results => {
        let processingUrls = []; 
        let successCount = 0;
        let errorMsg = '';
        
        // 2. 遍历结果：只收集成功的 URL，不关心原索引
        results.forEach(result => {
          if (result.status === 'fulfilled') {
            // 直接将成功的 URL 推入数组（不考虑原顺序）
            processingUrls.push(result.value.url); 
            successCount++;
          } else {
            errorMsg += result.reason + '; ';
          }
        });
        app.globalData.processedImages=[];
        //2025年9月18日重要

        app.globalData.processedImages = processingUrls;
        // 7. 结果反馈（成功/失败提示）
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
        wx.switchTab({
          url: '/pages/showpic/showpic',
        })
        wx.hideLoading(); 
      });
  }


})