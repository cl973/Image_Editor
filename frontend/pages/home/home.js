// pages/home/home.js
const app=getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    tip: '', // 上传状态提示
    previewUrls:[],
    currentTime: '', // 当前时间（时:分:秒）
    currentDate: '' 
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    // 页面加载时立即更新一次时间
    this.updateTime();
    // 每秒更新一次时间
    this.timeInterval = setInterval(() => {
      this.updateTime();
    }, 1000);
  },
  updateTime() {
    const date = new Date();
    
    // 格式化时间（时:分:秒，补0）
    const hours = this.formatNumber(date.getHours());
    const minutes = this.formatNumber(date.getMinutes());
    const seconds = this.formatNumber(date.getSeconds());
    const currentTime = `${hours}:${minutes}:${seconds}`;

    // 格式化日期（年-月-日 星期X）
    const year = date.getFullYear();
    const month = this.formatNumber(date.getMonth() + 1); // 月份从0开始，需+1
    const day = this.formatNumber(date.getDate());
    const week = ['日', '一', '二', '三', '四', '五', '六'][date.getDay()];
    const currentDate = `${year}-${month}-${day} 星期${week}`;

    // 更新数据到页面
    this.setData({
      currentTime,
      currentDate
    });
  },

  // 数字补0（如 9 → 09）
  formatNumber(n) {
    n = n.toString();
    return n[1] ? n : `0${n}`;
  },

  // 页面卸载时清除定时器（避免内存泄漏）
  onUnload() {
    clearInterval(this.timeInterval);
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
    this.setData({
      previewUrls:[]
    })
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

  chooseAndUploadPhoto() {
    const that = this;
    const currentCount = this.data.previewUrls.length;
  
    // 新增：若已有图片（长度≥1），提示“只能选1张，将替换当前图片”
    if (currentCount >= 1) {
      wx.showModal({
        title: '提示',
        content: '只能选择1张图片，是否替换当前图片？',
        confirmText: '替换',
        success: (res) => {
          if (!res.confirm) return; // 用户取消，不继续
          // 确认替换：先清空已有图片
          that.setData({ previewUrls: [] });
          app.globalData.originalImages = [];
          // 清空后，执行选图逻辑（下面的选图代码可抽成函数，避免重复）
          that.doChooseImage(); 
        }
      });
      return;
    }
  
    // 原选图逻辑抽成函数 doChooseImage()
    this.doChooseImage();
  },
  
  // 新增：抽离的选图逻辑
  doChooseImage() {
    const that = this;
    wx.chooseImage({
      count: 1,
      sizeType: ['original', 'compressed'],
      sourceType: ['album', 'camera'],
      success: function (chooseRes) {
        const tempFilePaths = chooseRes.tempFilePaths;
        tempFilePaths.forEach(tempFilePath => {
          wx.cropImage({
            src: tempFilePath,
            cropScale: null,
            maxHeight: 2000,
            maxWidth: 2000,
            minHeight: 100,
            minWidth: 100,
            success: function (cropRes) {
              const croppedFilePath = cropRes.tempFilePath;
              const newPreviewUrls = [croppedFilePath]; // 直接赋值（不concat，避免累计）
              app.globalData.originalImages = newPreviewUrls;
              that.setData({
                previewUrls: newPreviewUrls,
                tip: `已选择 1/1 张图片`
              });
            },
            fail: function (cropErr) {
              that.setData({ tip: '裁剪失败' });
              console.error('裁剪错误：', cropErr);
            }
          });
        });
      },
      fail: function (chooseErr) {
        that.setData({ tip: '未选择图片' });
        console.error('选图错误：', chooseErr);
      }
    });
  }
})


        // ---------------------- 可选：取消下面注释以开启上传 ----------------------
        // wx.uploadFile({
        //   url: 'http://1.15.143.65/upload', // 后端接口地址（需替换）
        //   filePath: croppedFilePath,
        //   name: 'originalpic',
        //   header: {
        //     'content-type': 'multipart/form-data'
        //   },
        //   success: (uploadRes) => {
        //     const result = JSON.parse(uploadRes.data);
        //     if (result.code === 200) {
        //       that.setData({
        //         tip: '上传成功！照片地址：' + result.data.photoUrl
        //       });
        //       app.globalData.originalImage = result.data.photoUrl;
        //     } else {
        //       that.setData({ tip: '上传失败：' + result.msg });
        //     }
        //   },
        //   fail: (err) => {
        //     that.setData({ tip: '上传失败：请检查网络' });
        //     console.error('上传错误：', err);
        //   }
        // });
