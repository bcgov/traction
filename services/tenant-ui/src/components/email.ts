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
    let transporter = nodemailer.createTransport({
      host: SERVER,
      port: PORT,
      secure: false,
    });

    let info = await transporter.sendMail({
      from: FROM,
      to: req.body.contact_email,
      subject: "Your reservation details", // Subject line
      html: `<h2>We recieved your reservation</h2> <p>Your reservation details are: <br> ID: ${req.body.reservationId} <br> PW: ${req.body.reservationPassword}`, // html body
    });

    return info;
  } catch (error) {
    console.error(`Error sending email: ${error}`);
    throw error;
  }
};
