// pages/editor1/editor1.js
const app=getApp()

Page({

 

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



// pages/uploadPhoto/uploadPhoto.js

  data: {
    previewUrls:[], // 照片预览地址
    tip: '' // 上传状态提示
  },
  onShow() {

    this.setData({
      previewUrls: app.globalData.originalImages || [] 
    });
  },

  // 选择照片并上传
  
  ImageDenoising(){
    this.setData({
      previewUrls:app.globalData.originalImages
    })
    this.processImage('ltpfx')
  },
  ImageEnhancement(){
    this.setData({
      previewUrls:app.globalData.originalImages
    })
    this.processImage2()
  },

processImage2(){
  const that = this;
    const { previewUrls } = this.data;
    
    // 检查是否有图片
    if (!previewUrls || previewUrls.length === 0) {
      this.setData({ tip: '请先选择照片' });
      return;
    }
  
    // 初始化处理状态（修复模板字符串引号问题）
    this.setData({
      tip: `正在处理 ${previewUrls.length} 张图片...`, // 用反引号包裹
      processedUrls: []
    });

    
    const originalImages = app.globalData.originalImages || []; // 全局图片数组
    

  
    // 2. 校验：全局图片数组是否有内容（替代原单个imagePath的校验）
    if (!originalImages.length) {
      wx.showToast({
        title: '请先选择图片（全局数组为空）',
        icon: 'none',
        duration: 2000
      });
      return;
    }
  

    const type = 'ltpfx'; 
  
    wx.showLoading({
      title: `上传中（共${originalImages.length}张）...`,
      mask: true
    });
  
    // 4. 单个图片上传函数（逻辑不变，仅参数适配全局数组）
    const uploadWithParams = (filePath, index) => {
      return new Promise((resolve, reject) => {
        wx.uploadFile({
          url: "http://1.15.143.65:8000/image-process", // 端口不变
          filePath: filePath, 
          name: 'image', 
          header: {
            'content-type': 'multipart/form-data'
          },
          formData: {  // 携带四个参数 + type + 图片索引（方便后端区分图片）
            'type': type, // 已修复：使用定义好的type值

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
        app.globalData.processedImages = [];
        //重要2025年9月18日

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
        wx.hideLoading(); 
        wx.switchTab({
          url: '/pages/showpic/showpic',
        })
       
      });
},

  processImage1(type) {
    const that = this;
    const { previewUrls } = this.data;
    
    // 检查是否有图片
    if (!previewUrls || previewUrls.length === 0) {
      this.setData({ tip: '请先选择照片' });
      return;
    }
  
    // 初始化处理状态（修复模板字符串引号问题）
    this.setData({
      tip: `正在处理 ${previewUrls.length} 张图片...`, // 用反引号包裹
      processedUrls: []
    });
    wx.navigateTo({
      url: '/pages/ltpfx/ltpfx',
      fail: (res) => {
        this.setData({
          tip:'跳转失败，请重试...'
        })
      },
    })
    // // 单个图片上传函数
    // const uploadSingleImage = (filePath, index) => {
    //   return new Promise((resolve, reject) => {
    //     wx.uploadFile({ 
    //       url: "http://1.15.143.65:8000/image-process",
    //       filePath: filePath,
    //       name: 'image',
    //       header: {
    //         'content-type': 'multipart/form-data'
    //       },
    //       formData: {
    //         'type': type,
    //         'index': index
    //       },
    //       success: (res) => {
    //         try {
    //           // 假设服务器返回格式：{ "success": true, "imageUrl": "xxx" } 或 { "success": false }
    //           const result = JSON.parse(res.data);
              
    //           // 核心修改：根据bool值判断成功与否（不再依赖code）
    //           if (result.success && result.imageUrl) {
    //             // 成功：返回索引和图片url
    //             resolve({
    //               index: index,
    //               url: result.imageUrl
    //             });
    //           } else {
    //             reject(`第${index+1}张处理失败：${result.msg || '处理未通过'}`);
    //           }
    //         } catch (e) {
    //           reject(`第${index+1}张解析失败：服务器返回格式错误`);
    //         }
    //       },
    //       fail: (err) => {
    //         reject(`第${index+1}张上传失败：网络错误`); // 修复模板字符串引号
    //       }
    //     });
    //   });
    // };
  
    // // 批量上传所有图片
    // const uploadPromises = previewUrls.map((filePath, index) => {
    //   return uploadSingleImage(filePath, index);
    // });
  
    // // 处理所有上传结果
    // Promise.allSettled(uploadPromises).then(results => {
    //   const processedUrls = new Array(previewUrls.length);
    //   let successCount = 0;
    //   let errorMsg = '';
  
    //   results.forEach(result => {
    //     if (result.status === 'fulfilled') {
    //       const { index, url } = result.value;
    //       processedUrls[index] = url;
    //       successCount++;
    //     } else {
    //       errorMsg += result.reason + '; ';
    //     }
    //   });
  
    //   // 更新页面状态（修复模板字符串引号）
    //   that.setData({
    //     processedUrls: processedUrls,
    //     tip: successCount > 0 
    //       ? `处理完成：成功${successCount}/${previewUrls.length}张` 
    //       : `全部处理失败：${errorMsg}`
    //   });
    // });
  }


});