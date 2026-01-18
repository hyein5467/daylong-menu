const multer = require("multer");
const { CloudinaryStorage } = require("multer-storage-cloudinary");
const cloudinary = require("./cloudinary");

const storage = new CloudinaryStorage({
  cloudinary,
  params: (req, file) => {
    const safeName = (req.body.name || "temp")
      .trim()
      .replace(/\s+/g, "_");

    return {
      public_id: safeName,        
      allowed_formats: ["png", "jpg", "jpeg"],
      overwrite: true,
    };
  },
});

module.exports = multer({ storage });
