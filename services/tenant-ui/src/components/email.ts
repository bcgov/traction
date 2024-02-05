import { Request } from "express";
import config from "config";
import nodemailer from "nodemailer";
import { Eta } from "eta"; // HTML templating engine
import { buildStatusAutofill } from "../helpers";

import { RESERVATION_APPROVED_TENANT_TEMPLATE } from "./email_templates/reservation_approved_tenant";
import { RESERVATION_DECLINED_TENANT_TEMPLATE } from "./email_templates/reservation_declined_tenant";
import { RESERVATION_RECIEVED_INNKEEPER_TEMPLATE } from "./email_templates/reservation_received_innkeeper";
import { RESERVATION_RECIEVED_TENANT_TEMPLATE } from "./email_templates/reservation_received_tenant";
import { RESERVATION_STATUSES } from "../helpers/constants";

const SERVER: string = config.get("server.smtp.server");
const PORT: number = config.get("server.smtp.port");
const FROM: string = config.get("server.smtp.senderAddress");
const SECURE: boolean = config.get("server.smtp.secure");
const USER: string = config.get("server.smtp.user");
const PASSWORD: string = config.get("server.smtp.password");
const INNKEEPER: string = config.get("server.smtp.innkeeperInbox");

const eta = new Eta();

/**
 * @function stringOrBooleanTruthy
 * Returns true if the value is a string "true" or a boolean true, returns false otherwise
 * @returns {boolean}
 */
export function stringOrBooleanTruthy(value: string | boolean) {
  return value === 'true' || value === true;
}

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
      secure: stringOrBooleanTruthy(SECURE),
      auth: {
        user: USER,
        pass: PASSWORD,
      },
    });

    req.body.serverUrlStatusRouteAutofill = buildStatusAutofill(req.body);
    const tenantHtml = eta.renderString(RESERVATION_RECIEVED_TENANT_TEMPLATE, req);

    // Send a confirmation email to the person doing the reservation
    await transporter.sendMail({
      from: FROM,
      to: req.body.contactEmail,
      subject: "[TRACTION] Reservation Received",
      html: tenantHtml, // html body
    });

    const innkeeperHtml = eta.renderString(
      RESERVATION_RECIEVED_INNKEEPER_TEMPLATE,
      req
    );

    // Send a notification email to the Innkeeper team
    await transporter.sendMail({
      from: FROM,
      to: INNKEEPER,
      subject: `[TRACTION] Reservation Request - ${req.body.contactName}`,
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
      secure: stringOrBooleanTruthy(SECURE),
      auth: {
        user: USER,
        pass: PASSWORD,
      },
    });

    let template;
    let subject;
    if (req.body.state === RESERVATION_STATUSES.APPROVED) {
      template = RESERVATION_APPROVED_TENANT_TEMPLATE;
      subject = "[TRACTION] Reservation Approved!";
      req.body.serverUrlStatusRouteAutofill = buildStatusAutofill(req.body);
    } else if (req.body.state === RESERVATION_STATUSES.DENIED) {
      template = RESERVATION_DECLINED_TENANT_TEMPLATE;
      subject = "[TRACTION] Reservation Declined!";
    } else {
      throw Error(`Unsupported reservation state: ${req.body.state}`);
    }
    const tenantHtml = eta.renderString(template, req);

    // Send a status update email to the applicant
    await transporter.sendMail({
      from: FROM,
      to: req.body.contactEmail,
      subject,
      html: tenantHtml, // html body
    });
  } catch (error) {
    console.error(`Error sending email: ${error}`);
    throw error;
  }
};
