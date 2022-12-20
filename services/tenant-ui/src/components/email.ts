import { Request } from "express";
import config from "config";
import nodemailer from "nodemailer";
const SERVER: string = config.get("server.smtp.server");
const PORT: number = config.get("server.smtp.port");
const FROM: string = config.get("server.smtp.senderAddress");
const INNKEEPER: string = config.get("server.smtp.innkeeperInbox");

/**
 * @function sendEmail
 * Send one of the preconfigured emails as part of the reservation flow
 * @returns {string} The inkeeper token
 */
export const sendEmail = async (req: Request) => {
  try {
    const transporter = nodemailer.createTransport({
      host: SERVER,
      port: PORT,
      secure: false,
    });

    const info = await transporter.sendMail({
      from: FROM,
      to: INNKEEPER,
      subject: "Your reservation details",
      text: `Hello, your reservation was recieved. Your reservation ID is ${123} and your password is ${123}`,
    });

    return info;
  } catch (error) {
    console.error(`Error sending email: ${error}`);
    throw error;
  }
};
