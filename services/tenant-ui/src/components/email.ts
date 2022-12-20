import { Request } from "express";
import config from "config";
import nodemailer from "nodemailer";
const TRACURL: string = config.get("server.tractionUrl");
const INN_USER = config.get("server.innkeeper.user");
const INN_PW = config.get("server.innkeeper.key");

/**
 * @function sendEmail
 * Send one of the preconfigured emails as part of the reservation flow
 * @returns {string} The inkeeper token
 */
export const sendEmail = async (req: Request) => {
  try {
    let transporter = nodemailer.createTransport({
      host: "apps.smtp.gov.bc.ca",
      port: 25,
      secure: false,
    });

    let info = await transporter.sendMail({
      from: "DoNotReplyTraction@gov.bc.ca", // sender address
      to: "lucas.oneil@gov.bc.ca", // list of receivers
      subject: "Hello ✔", // Subject line
      text: "Hello world?", // plain text body
      html: "<b>Hello world?</b>", // html body
    });

    return info;
  } catch (error) {
    console.error(`Error sending email: ${error}`);
    throw error;
  }
};
