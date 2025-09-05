import mongoose from "mongoose";

const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  profileImageUrl: { type: String, default: "" },
  verifyOtp: { type: String, default: "" }, // 账号初次使用验证码
  verifyOtpExpireAt: { type: Number, default: 0 }, // 验证码过期时间
  isAccountVerified: { type: Boolean, default: false }, // 账号是否验证
  resetOtp: { type: String, default: "" }, // 重置密码验证码
  resetOtpExpireAt: { type: Number, default: 0 }, // 重置密码验证码过期时间
});

const userModel = mongoose.models.user || mongoose.model("user", userSchema);

export default userModel;
