// pages/editor2/editor2.js
Page({

  /**
   * 页面的初始数据
   */
  data: {

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

  }
})

Page({
  data: {
    previewUrl: '', // 照片预览地址
    tip: '' // 上传状态提示
  },

  // 选择照片并上传
  chooseAndUploadPhoto() {
    const that = this;

    // 1. 调用微信API选择/拍摄照片
    wx.chooseImage({
      count: 1, // 最多选择1张照片
      sizeType: ['original', 'compressed'], // 支持原图/压缩图
      sourceType: ['album', 'camera'], // 支持相册/相机
      success: function (res) {
        // 选图成功：获取临时文件路径（关键！）
        const tempFilePath = res.tempFilePaths[0];
        
        // 2. 显示照片预览
        that.setData({
          previewUrl: tempFilePath,
          tip: '正在上传...'
        });

        // 3. 调用微信API上传文件到服务器
        wx.uploadFile({
          url: 'http://1.15.143.65/upload-api', // 服务器上传接口地址（需替换为后端实际接口）
          filePath: tempFilePath, // 要上传的文件临时路径
          name: 'file', // 后端接收文件时的参数名（需与后端一致，如"image"）
          header: {
            'content-type': 'multipart/form-data' // 固定格式，文件上传必须
          },
          // 可选：额外传递给后端的参数（如用户ID、照片类型）
          formData: {
      
            'photoType': 'originalpic' // 示例：照片类型（头像/证件照等）
          },
          success: function (uploadRes) {
            // 上传成功：处理服务器返回的结果（需根据后端格式解析）
            const result = JSON.parse(uploadRes.data); // 假设后端返回JSON格式
            if (result.code === 200) { // 假设200为成功状态码
              that.setData({
                tip: '上传成功！照片地址：' + result.data.photoUrl // 后端返回的照片存储地址
              });
            } else {
              that.setData({
                tip: '上传失败：' + result.msg // 后端返回的错误信息
              });
            }
          },
          fail: function (err) {
            // 上传失败：网络错误、服务器无响应等
            that.setData({
              tip: '上传失败：请检查网络或服务器状态'
            });
            console.error('上传错误详情：', err); // 打印错误日志便于调试
          },
          complete: function () {
            // 无论成功/失败，都会执行（如隐藏加载动画）
          }
        });
      },
      fail: function (err) {
        // 选图失败：用户取消、权限不足等
        that.setData({
          tip: '未选择照片'
        });
        console.error('选图错误详情：', err);
      }
    });
  }
});