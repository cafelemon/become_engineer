import assert from "node:assert/strict";

function parseDockerRun(tokens) {
  assert.deepEqual(tokens.slice(0, 2), ["docker", "run"], "command must start with docker run");

  const result = {
    command: "docker run",
    remove: false,
    name: null,
    port: null,
    mount: null,
    environment: {},
    image: null,
  };

  for (let index = 2; index < tokens.length; index += 1) {
    const token = tokens[index];

    if (token === "--rm") {
      result.remove = true;
      continue;
    }

    if (token === "--name") {
      result.name = tokens[index + 1];
      index += 1;
      continue;
    }

    if (token === "-p") {
      const [hostIp, hostPort, containerPort] = tokens[index + 1].split(":");
      result.port = { hostIp, hostPort, containerPort };
      index += 1;
      continue;
    }

    if (token === "--mount") {
      const fields = Object.fromEntries(
        tokens[index + 1].split(",").map((entry) => {
          const separator = entry.indexOf("=");
          return separator === -1
            ? [entry, true]
            : [entry.slice(0, separator), entry.slice(separator + 1)];
        }),
      );
      result.mount = fields;
      index += 1;
      continue;
    }

    if (token === "--env") {
      const entry = tokens[index + 1];
      const separator = entry.indexOf("=");
      assert.notEqual(separator, -1, "environment entry must contain =");
      result.environment[entry.slice(0, separator)] = entry.slice(separator + 1);
      index += 1;
      continue;
    }

    assert.equal(index, tokens.length - 1, `unexpected token: ${token}`);
    result.image = token;
  }

  return result;
}

function assertSafeLearningCommand(command, expected) {
  assert.equal(command.remove, true, "learning container must be removed after exit");
  assert.equal(command.port.hostIp, "127.0.0.1", "preview port must bind to loopback");
  assert.equal(command.port.hostPort, expected.hostPort);
  assert.equal(command.port.containerPort, "80");
  assert.equal(command.mount.type, "bind");
  assert.equal(command.mount.src, expected.source);
  assert.equal(command.mount.dst, "/workspace/notes");
  assert.equal(command.mount.readonly, true, "learning mount must be read-only");
  assert.equal(command.environment.APP_MODE, expected.mode);
  assert.equal(command.image, "demo-web:1.0");

  const environmentKeys = Object.keys(command.environment).join(" ").toUpperCase();
  assert.doesNotMatch(environmentKeys, /TOKEN|PASSWORD|SECRET|PRIVATE|API_KEY/);
}

const baseline = parseDockerRun([
  "docker", "run", "--rm", "--name", "be-preview",
  "-p", "127.0.0.1:8080:80",
  "--mount", "type=bind,src=/ABSOLUTE/PATH/learning-workspace/notes,dst=/workspace/notes,readonly",
  "--env", "APP_MODE=study",
  "demo-web:1.0",
]);

assert.equal(baseline.name, "be-preview");
assertSafeLearningCommand(baseline, {
  hostPort: "8080",
  source: "/ABSOLUTE/PATH/learning-workspace/notes",
  mode: "study",
});

const modified = parseDockerRun([
  "docker", "run", "--rm", "--name", "be-preview-review",
  "-p", "127.0.0.1:9090:80",
  "--mount", "type=bind,src=/ABSOLUTE/PATH/learning-workspace/practice,dst=/workspace/notes,readonly",
  "--env", "APP_MODE=review",
  "demo-web:1.0",
]);

assert.equal(modified.name, "be-preview-review");
assertSafeLearningCommand(modified, {
  hostPort: "9090",
  source: "/ABSOLUTE/PATH/learning-workspace/practice",
  mode: "review",
});

console.log(JSON.stringify({
  valid: true,
  commands_checked: 2,
  docker_invoked: false,
  network_used: false,
  loopback_only: true,
  readonly_mounts: true,
  secrets_present: false,
}, null, 2));
