import config from "config";
import { decode } from "jsonwebtoken";

// Move this allowedList to const file (or config?) as we add more (also unit test this logic)
const PROXYACAPYROOT: string = config.get("server.proxyAcapyPath");
const allowedList = [/^\/basicmessages$/, /^\/connections\/.*\/send-message$/];

export function handleAcapy(req: any, res: any, next: any) {
  // Since this app calls the acapy admin API, it will add that X-API-KEY header later
  // But we only want TENANTS to operate on calls they are allowed to, so we can't let people's
  // valid acapy tokens be put in a call to this api, and edit that call to proxy to an actual
  // acapy administrative call. So at this point we have to only let allowed endpoints through
  const justPath = req.originalUrl.split(PROXYACAPYROOT).pop().split("?")[0];
  const isMatch = allowedList.some((rx) => rx.test(justPath));
  if (!isMatch) return res.sendStatus(403);

  // Extract the ACAPY token from the TRACTION token (likely not needed down the line)
  const authHeader = req.headers["authorization"];
  const token = authHeader && authHeader.split(" ")[1];
  if (!token) return res.sendStatus(401);

  // We are only decoding, not verifying this token at this point. The token is forwarded
  // through to acapy where verification takes place so in this proxy app nothing should
  // be done with this token or used for any actual authentication
  req.parsedToken = decode(token);
  // Acapy's token is the "key" claim in the token from Traction
  if (!req.parsedToken.key) return res.sendStatus(401);
  next();
}
