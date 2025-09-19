const app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    tip: '',
    oriimages: [],
    proimages: [],
    pimage: "",
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
    // 处理空数组场景，避免pimage为undefined
    console.log("处理后图片",app.globalData.processedImages)
    const processedImages = app.globalData.processedImages || [];
    const originalImages = app.globalData.originalImages || [];
    this.setData({
      proimages: processedImages,
      oriimages: originalImages,
      pimage: processedImages[0] || ''
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
    // 下拉刷新时重新加载数据并停止刷新动画
    this.onShow();
    wx.stopPullDownRefresh();
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

  downloadProcessedImage() {
    // 修正变量名，确保语义准确
    const pimage = this.data.proimages[0];

    if (!pimage) {
      this.setData({
        tip: '没有可下载的处理后图片'
      });
      return;
    }

    this.setData({
      tip: '正在下载图片...'
    });

    // 先下载图片到本地临时路径
    wx.downloadFile({
      url: pimage,
      success: function (res) {
        // 下载成功后保存到相册
        wx.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: function () {
            wx.showToast({
              title: '下载成功',
              icon: 'success',
              duration: 2000
            });
          },
          fail: function (err) {
            console.error('保存图片失败：', err);
            // 处理授权失败情况
            if (err.errMsg.includes('auth deny')) {
              wx.showToast({
                title: '请开启保存相册权限',
                icon: 'none',
                duration: 2000
              });
            } else {
              wx.showToast({
                title: '保存失败',
                icon: 'none',
                duration: 2000
              });
            }
          }
        });
      },
      fail: function (err) {
        console.error('下载图片失败：', err);
        wx.showToast({
          title: '下载失败',
          icon: 'none',
          duration: 2000
        });
      }
    });
  }

})
