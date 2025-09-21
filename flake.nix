{
  description = "Using Nix Flake apps to run scripts with uv2nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    nixpkgs,
    uv2nix,
    pyproject-nix,
    pyproject-build-systems,
    systems,
    ...
  }: let
    inherit (nixpkgs) lib;

    # Create attrset for each system
    forAllSystems = lib.genAttrs (import systems);

    # Workspace and package setup
    workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};

    overlay = workspace.mkPyprojectOverlay {
      sourcePreference = "wheel";
    };

    pythonSets = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (pkgs.stdenv) mkDerivation;
        python = pkgs.python313;
        baseSet = pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        };
      in
        baseSet.overrideScope (
          lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
            (final: prev: {
              bff-demo = prev.bff-demo.overrideAttrs (old: {
                passthru =
                  (old.passthru or {})
                  // {
                    tests = let
                      virtualenv = final.mkVirtualEnv "bff-demo-pytest" {
                        bff-demo = ["dev"];
                      };
                    in
                      (old.tests or {})
                      // {
                        pytest = mkDerivation {
                          name = "${final.bff-demo.name}-pytest";
                          inherit (final.bff-demo) src;
                          nativeBuildInputs = [virtualenv];
                          dontConfigure = true;
                          buildPhase = ''
                            runHook preBuild
                            pytest --cov tests --cov-report html tests
                            runHook postBuild
                          '';
                          installPhase = ''
                            runHook preInstall
                            mv htmlcov $out
                            runHook postInstall
                          '';
                        };
                        pyrefly = mkDerivation {
                          name = "${final.bff-demo.name}-pyrefly";
                          inherit (final.bff-demo) src;
                          nativeBuildInputs = [virtualenv];
                          dontConfigure = true;
                          dontInstall = true;
                          buildPhase = ''
                            runHook preBuild
                            mkdir $out
                            pyrefly check --debug-info $out/pyrefly.json --output-format json --config pyproject.toml
                            runHook postBuild
                          '';
                        };
                        ruff = mkDerivation {
                          name = "${final.bff-demo.name}-ruff";
                          inherit (final.bff-demo) src;
                          nativeBuildInputs = [virtualenv];
                          dontConfigure = true;
                          buildPhase = ''
                            runHook preBuild
                            ruff check --ignore F401 --output-format json -o ruff.json
                            runHook postBuild
                          '';
                          installPhase = ''
                            runHook preInstall
                            mv ruff.json $out
                            runHook postInstall
                          '';
                        };
                      };
                  };
              });
            })
          ]
        )
    );
  in {
    packages = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      pythonSet = pythonSets.${system};
      venv = pythonSet.mkVirtualEnv "bff-demo-venv" workspace.deps.default;
      # alpine base docker image
      alpine = pkgs.dockerTools.pullImage {
        imageName = "alpine";
        imageDigest = "sha256:4bcff63911fcb4448bd4fdacec207030997caf25e9bea4045fa6c8c44de311d1";
        finalImageName = "alpine";
        finalImageTag = "latest";
        sha256 = "sha256-1Af8p6cYQs8sxlowz4BC6lC9eAOpNWYnIhCN7BSDKL0=";
        os = "linux";
        arch =
          if system == "x86_64-linux"
          then "amd64"
          else if system == "aarch64-linux"
          then "arm64"
          else system;
      };
      bff-demo-package = pkgs.stdenv.mkDerivation {
        name = "bff-demo-package";
        src = ./.;
        buildInputs = [venv];
        nativeBuildInputs = with pkgs; [tailwindcss_4 makeWrapper];
        installPhase = ''
          mkdir -p $out/app
          cp -r $src/app/* $out/app/

          chmod +w $out/app/style
          tailwindcss -i $src/app/style/input.css -o $out/app/style/output.css --minify
          chmod -w $out/app/style

          chmod +x $out/app/main.py $out/app/app.py
          patchShebangs $out/app/app.py

          chmod +w $out/app/main.py
          mv $out/app/main.py $out/app/main
          chmod -w $out/app/main

          wrapProgram $out/app/main --prefix PATH : ${pkgs.lib.makeBinPath [pkgs.valkey]}
        '';
      };
    in {
      default = bff-demo-package;
      container = pkgs.dockerTools.buildLayeredImage {
        name = "bff-demo-container";
        created = "now";
        fromImage = alpine;
        maxLayers = 125;
        contents = [pkgs.curl];
        config = {
          Cmd = ["${bff-demo-package}/app/main"];
          ExposedPorts = {"7999/tcp" = {};};
          Healthcheck = {
            Test = ["CMD-SHELL" "curl -f http://localhost:7999/health || exit 1"];
          };
        };
      };
    });

    # Dynamic script discovery for .sh and .py files
    apps = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonSet = pythonSets.${system};
        venv = pythonSet.mkVirtualEnv "bff-demo-venv" workspace.deps.default;
        inherit (pkgs.lib) filterAttrs hasSuffix mapAttrsToList genAttrs;

        # App discovery and creation
        appsBasedir = ./scripts;
        appFiles = filterAttrs (name: type: type == "regular" && (hasSuffix ".sh" name || hasSuffix ".py" name)) (
          builtins.readDir appsBasedir
        );
        appNames = mapAttrsToList (name: _: pkgs.lib.removeSuffix ".sh" (pkgs.lib.removeSuffix ".py" name)) appFiles;

        # Shared build logic for creating executable scripts
        makeExecutable = appName: ''
          mkdir -p $out/bin
          # Determine actual file path (sh takes precedence)
          if [ -f ${appsBasedir}/${appName}.sh ]; then
            cp ${appsBasedir}/${appName}.sh $out/bin/${appName}
          else
            cp ${appsBasedir}/${appName}.py $out/bin/${appName}
          fi
          chmod +x $out/bin/${appName}
          patchShebangs $out/bin/${appName}
        '';

        # Create individual apps
        makeApp = appName: {
          type = "app";
          program = "${pkgs.runCommand appName {buildInputs = [pkgs.bash venv];} (makeExecutable appName)}/bin/${appName}";
          meta = {description = "Run ${appName}";};
        };

        # Generate all script apps
        scriptApps = genAttrs appNames makeApp;
      in
        scriptApps // {default = scriptApps.fastapi-dev;}
    );

    devShells = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python313;
      pythonSet = pythonSets.${system};
      venv = pythonSet.mkVirtualEnv "bff-demo-dev-venv" workspace.deps.all;
      # tmux.conf file
      tmuxConf = pkgs.writeText "tmux.conf" ''
        set -g mouse on
        set-option -g default-command "${pkgs.bash}/bin/bash -l"
      '';
      # wrapper script for tmux
      wrappedTmux = pkgs.writeShellScriptBin "tmux" ''
        exec ${pkgs.tmux}/bin/tmux -f ${tmuxConf} "$@"
      '';
      # Packages to install in devShells
      devPackages = with pkgs;
        [
          bash
          jq
          uv
          tailwindcss_4
          valkey
          watchman
          posting
          mitmproxy
          duckdb
          yazi
          lazydocker
          brave
          firefox
        ]
        ++ (lib.optionals pkgs.stdenv.isLinux [chromium])
        ++ [wrappedTmux];
    in {
      # This devShell simply adds Python & uv and undoes the dependency leakage done by Nixpkgs Python infrastructure.
      impure = pkgs.mkShell {
        packages =
          [
            python
          ]
          ++ devPackages;
        env =
          {
            UV_PYTHON_DOWNLOADS = "never";
            UV_PYTHON = python.interpreter;
          }
          // lib.optionalAttrs pkgs.stdenv.isLinux {
            LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
          };
        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
          export SELL=$(which bash)
          uv sync
          source .venv/bin/activate
        '';
      };
      # This devShell uses uv2nix to construct a virtual environment purely from Nix, using the same dependency specification as the application.
      default = pkgs.mkShell {
        packages =
          [
            venv
          ]
          ++ devPackages;
        env = {
          UV_NO_SYNC = "1";
          UV_PYTHON = python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
        };
        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
          export SELL=$(which bash)
          export VIRTUAL_ENV=${venv}
          source ${venv}/bin/activate
          source ${./scripts/vscode.sh} # Configure VS Code
        '';
      };
    });

    # Construct flake checks from Python set
    checks = forAllSystems (system: let
      pythonSet = pythonSets.${system};
    in {
      inherit (pythonSet.bff-demo.passthru.tests) pytest pyrefly ruff;
    });

    formatter = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
      in
        pkgs.alejandra
    );
  };
}
