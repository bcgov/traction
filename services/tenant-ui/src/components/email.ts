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

    // Send a confirmation email to the person doing the reservation
    await transporter.sendMail({
      from: FROM,
      to: req.body.contact_email,
      subject: "Your reservation details", // Subject line
      html: `<h2>We recieved your reservation</h2> <p>Your reservation details are: <br> ID: ${req.body.reservationId} <br> PW: ${req.body.reservationPassword}</p>`, // html body
    });

    // Send a notification email to the Innkeeper team
    await transporter.sendMail({
      from: FROM,
      to: INNKEEPER,
      subject: "New tenant reservation", // Subject line
      html: `<h2>There is a new tenant reservation request</h2> <p>${req.body.contact_email} has requested a tenant</p>`, // html body
    });

  } catch (error) {
    console.error(`Error sending email: ${error}`);
    throw error;
  }
};
