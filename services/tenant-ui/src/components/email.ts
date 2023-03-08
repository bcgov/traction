import { Request } from "express";
import config from "config";
import nodemailer from "nodemailer";
import * as eta from "eta"; // HTML templating engine

import { RESERVATION_APPROVED_TENANT_TEMPLATE } from "./email_templates/reservation_approved_tenant";
import { RESERVATION_DECLINED_TENANT_TEMPLATE } from "./email_templates/reservation_declined_tenant";
import { RESERVATION_RECIEVED_INNKEEPER_TEMPLATE } from "./email_templates/reservation_received_innkeeper";
import { RESERVATION_RECIEVED_TENANT_TEMPLATE } from "./email_templates/reservation_received_tenant";

const SERVER: string = config.get("server.smtp.server");
const PORT: number = config.get("server.smtp.port");
const FROM: string = config.get("server.smtp.senderAddress");
const INNKEEPER: string = config.get("server.smtp.innkeeperInbox");

/**
 * @function sendConfirmationEmail
 * Send the preconfigured emails when a reservation is created
 * @returns {string} The inkeeper token
 */
export const sendConfirmationEmail = async (req: Request) => {
  try {
    const transporter = nodemailer.createTransport({
      host: SERVER,
      port: PORT,
      secure: false,
    });

    const tenantHtml = eta.render(RESERVATION_RECIEVED_TENANT_TEMPLATE, req);

    // Send a confirmation email to the person doing the reservation
    await transporter.sendMail({
      from: FROM,
      to: req.body.contactEmail,
      subject: "Your reservation details",
      html: tenantHtml, // html body
    });

    const innkeeperHtml = eta.render(
      RESERVATION_RECIEVED_INNKEEPER_TEMPLATE,
      req
    );

    // Send a notification email to the Innkeeper team
    await transporter.sendMail({
      from: FROM,
      to: INNKEEPER,
      subject: "New tenant reservation",
      html: innkeeperHtml, // html body
    });
  } catch (error) {
    console.error(`Error sending email: ${error}`);
    throw error;
  }
};

/**
 * @function sendStatusEmail
 * Send the preconfigured emails as part of the reservation flow
 * @returns {string} The inkeeper token
 */
export const sendStatusEmail = async (req: Request) => {
  try {
    const transporter = nodemailer.createTransport({
      host: SERVER,
      port: PORT,
      secure: false,
    });

    const template = req.body.state.match(/approved/i)
      ? RESERVATION_APPROVED_TENANT_TEMPLATE
      : RESERVATION_DECLINED_TENANT_TEMPLATE;

    const tenantHtml = eta.render(template, req);

    // Send a status update email to the applicant
    await transporter.sendMail({
      from: FROM,
      to: req.body.contactEmail,
      subject: "Your reservation details",
      html: tenantHtml, // html body
    });
  } catch (error) {
    console.error(`Error sending email: ${error}`);
    throw error;
  }
};
